{
  description = "Automatically send reminder emails to students with missing quizzes";

  inputs.nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";

  outputs = { self, nixpkgs, ... }:
    let
      system = "x86_64-linux";
      pkgs = import nixpkgs { inherit system; };
      moodlepy = with pkgs.python311Packages;
        buildPythonPackage rec {
          pname = "moodlepy";
          version = "v0.24.0";
          src = pkgs.fetchFromGitHub {
            owner = "hexatester";
            repo = "moodlepy";
            rev = version;
            sha256 = "sha256-eUUAQu0//ILnplbp5zq/a63o7ibsK7gBzdJCgdxeBz8=";
          };
          doCheck = false;
          propagatedBuildInputs = [ attrs cattrs requests ujson ];
        };
    in {
      packages.${system}.default = with pkgs.python311Packages;
        buildPythonApplication {
          name = "auto_reminder";
          version = "0.0.1";
          src = ./.;
          format = "pyproject";
          buildInputs = [ setuptools ];
          propagatedBuildInputs = [ moodlepy aiosmtplib ];
        };

      formatter.${system} = pkgs.nixpkgs-fmt;

      devShells.${system}.default = pkgs.mkShell {
        buildInputs = [
          (pkgs.python3.withPackages (py-pkgs: with py-pkgs; [
            requests
            moodlepy
            aiosmtplib
            jedi-language-server
          ]))
        ];
      };
    };
}
