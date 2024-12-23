{
  inputs = {
    utils.url = "github:numtide/flake-utils";
    # NOTE: We need to use tree-sitter <0.24 (as contained in this release) because otherwise
    # the grammar packages lag behind and can't be picked up
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-24.05";
    pyproject-nix = {
      url = "github:pyproject-nix/pyproject.nix";
      inputs.nixpkgs.follows = "nixpkgs";
    };
    uv2nix = {
      url = "github:pyproject-nix/uv2nix";
      inputs.pyproject-nix.follows = "pyproject-nix";
      inputs.nixpkgs.follows = "nixpkgs";
    };
    pyproject-build-systems = {
      url = "github:pyproject-nix/build-system-pkgs";
      inputs.pyproject-nix.follows = "pyproject-nix";
      inputs.uv2nix.follows = "uv2nix";
      inputs.nixpkgs.follows = "nixpkgs";
    };
  };

  outputs = { self, nixpkgs, utils, pyproject-nix, uv2nix, pyproject-build-systems }:
    utils.lib.eachDefaultSystem (system:
      let
        pkgs = import nixpkgs {
          inherit system;
        };

        grammars = with pkgs.tree-sitter.builtGrammars; [
          tree-sitter-python
        ];

        # Container for the source packages
        grammars-pkg = pkgs.linkFarm "grammars" (map (g: { name = g.pname; path = g.src.outPath; }) grammars);

        # Config for tree-sitter to find the source packages
        tree-sitter-config = pkgs.writeTextFile {
          name = "tree-sitter-config";
          destination = "/config.json";
          text = builtins.toJSON { "parser-directories" = [grammars-pkg.outPath ]; };
        };

      # Load a uv workspace from a workspace root.
      # Uv2nix treats all uv projects as workspace projects.
      workspace = uv2nix.lib.workspace.loadWorkspace { workspaceRoot = ./.; };

      # Create package overlay from workspace.
      overlay = workspace.mkPyprojectOverlay {
        # Prefer prebuilt binary wheels as a package source.
        # Sdists are less likely to "just work" because of the metadata missing from uv.lock.
        sourcePreference = "wheel"; # or sourcePreference = "sdist";
      };

      # Extend generated overlay with build fixups
      pyprojectOverrides = _final: _prev: {
        # Implement build fixups here.
      };

      # Use a slightly older Python to ensure compatibility
      python = pkgs.python311;

      pythonSet =
        # Use base package set from pyproject.nix builders
        (pkgs.callPackage pyproject-nix.build.packages {
          inherit python;
        }).overrideScope
          (
            nixpkgs.lib.composeManyExtensions [
              pyproject-build-systems.overlays.default
              overlay
              pyprojectOverrides
            ]
          );

      in {
      formatter = pkgs.nixfmt-rfc-style;

      # Package a virtual environment as our main application. No optional dependencies for production.
      # packages.${system}.default = pythonSet.mkVirtualEnv "prod-env" workspace.deps.default;
      devShell =
        # This devShell uses uv2nix to construct a virtual environment purely from Nix, using the same dependency specification as the application.
        # The notable difference is that we also apply another overlay here enabling editable mode ( https://setuptools.pypa.io/en/latest/userguide/development_mode.html ).
        #
        # This means that any changes done to your local files do not require a rebuild.
          let
            # Create an overlay enabling editable mode for all local dependencies.
            editableOverlay = workspace.mkEditablePyprojectOverlay {
              # Use environment variable
              root = "$REPO_ROOT";
              # Optional: Only enable editable for these packages
              # members = [ "doclint" ];
            };
            # Override previous set with our overrideable overlay.
            editablePythonSet = pythonSet.overrideScope editableOverlay;
            # Build virtual environment, with local packages being editable.
            virtualenv = editablePythonSet.mkVirtualEnv "dev-env" workspace.deps.all;

          in
          pkgs.mkShell {
          buildInputs = [
            pkgs.tree-sitter  # We don't use withPlugins because we want the source packages, rather than built
            grammars-pkg
          ];
            packages = [
              virtualenv
              pkgs.uv
            ];
            shellHook = ''
              export TREE_SITTER_DIR=${tree-sitter-config}
              # Undo dependency propagation by nixpkgs.
              unset PYTHONPATH

              # Don't create venv using uv
              export UV_NO_SYNC=1

              # Prevent uv from downloading managed Python's
              export UV_PYTHON_DOWNLOADS=never

              # Get repository root using git. This is expanded at runtime by the editable `.pth` machinery.
              export REPO_ROOT=$(git rev-parse --show-toplevel)
            '';
          };
      });
}
