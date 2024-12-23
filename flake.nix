{
  inputs = {
    utils.url = "github:numtide/flake-utils";
    # NOTE: We need to use tree-sitter <0.24 (as contained in this release) because otherwise
    # the grammar packages lag behind and can't be picked up
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-24.05";
  };

  outputs = { self, nixpkgs, utils }:
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
      in {

        devShell = pkgs.mkShell {
          buildInputs = [
            pkgs.tree-sitter  # We don't use withPlugins because we want the source packages, rather than built
            grammars-pkg
          ];

          # Decorative prompt override so we know when we're in a dev shell
          shellHook = ''
            export TREE_SITTER_DIR=${tree-sitter-config}
          '';
        };
      });
}
