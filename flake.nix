{
  description = "Automatically send reminder emails to students with missing quizzes";

  inputs.nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";

  outputs = { self, nixpkgs, ... }:
    let
      system = "x86_64-linux";
      pkgs = import nixpkgs { inherit system; };
      moodlepy = with pkgs.python311Packages;
        (buildPythonPackage rec {
          pname = "moodlepy";
          version = "v0.24.0";
          src = pkgs.fetchFromGitHub {
            owner = "hexatester";
            repo = "moodlepy";
            rev = version;
            sha256 = "sha256-eUUAQu0//ILnplbp5zq/a63o7ibsK7gBzdJCgdxeBz8=";
          };
          doCheck = false;
        });
    in {
      packages.${system}.default = let
        name = "auto_reminder";
        version = "0.1.0";
        pyproject = (pkgs.formats.toml { }).generate "pyproject.toml" {
          project = {
            inherit name version;
            readme = "README.md";
          };
        };
      in with pkgs.python311Packages; buildPythonPackage {
        inherit name version;
        src = ./.;
        format = "pyproject";
        preBuild = "cp ${pyproject} pyproject.toml";
        buildInputs = [ setuptools requests moodlepy ];
      };

      formatter.${system} = pkgs.nixpkgs-fmt;

      devShells.${system}.default = pkgs.mkShell {
        buildInputs = [
          (pkgs.python3.withPackages (py-pkgs: with py-pkgs; [
            requests
            moodlepy
            jedi-language-server
          ]))
        ];
      };
    };
}
