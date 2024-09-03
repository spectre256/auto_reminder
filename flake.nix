# Copyright 2024 Ellis Gibbons
#
# Rose-Hulman Institute of Technology, hereby disclaims all copyright interest
# in the program "auto_reminder" written by Ellis Gibbons.
#
# Dr. Jason Yoder 21 May 2024
# Jason Yoder, Professor
#
# This file is part of auto_reminder.
#
# auto_reminder is free software: you can redistribute it and/or modify it under the
# terms of the GNU General Public License as published by the Free Software
# Foundation, either version 3 of the License, or (at your option) any later
# version.
#
# auto_reminder is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
# A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with
# auto_reminder. If not, see <https://www.gnu.org/licenses/>.

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
      auto_reminder = with pkgs.python311Packages;
        buildPythonApplication {
          name = "auto_reminder";
          version = "0.0.1";
          src = ./.;
          format = "pyproject";
          buildInputs = [ setuptools ];
          propagatedBuildInputs = [ moodlepy aiosmtplib ];
        };
    in {
      packages.${system} = {
        default = auto_reminder;

        docker = let
          crontab = pkgs.writeTextDir "/etc/crontab" (builtins.readFile ./crontab);
        in pkgs.dockerTools.buildImage {
          name = "auto_reminder";
          tag = "latest";
          copyToRoot = pkgs.buildEnv {
            name = "root";
            paths = [ auto_reminder crontab pkgs.supercronic ];
            pathsToLink = [ "/bin" "/etc" ];
          };
          config.Cmd = [ "/bin/supercronic" "/etc/crontab" ];
        };
      };

      formatter.${system} = pkgs.nixpkgs-fmt;

      devShells.${system}.default = pkgs.mkShell {
        buildInputs = with pkgs; [
          (python3.withPackages (py-pkgs: with py-pkgs; [
            requests
            moodlepy
            aiosmtplib
            jedi-language-server
          ]))
          supercronic
        ];
      };
    };
}
