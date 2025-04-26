{
  description = "Python script to run the Discord bot with a token and output directory.";

  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils }: flake-utils.lib.eachDefaultSystem (system: let
    pkgs = import nixpkgs { inherit system; };
    python = pkgs.python313;
  in {
    packages.default = pkgs.python3Packages.buildPythonApplication rec {
      pname = "freelancer_export_script";  # Match setup.py name
      version = "1.0.0";
      
      src = ./.;
      
      nativeBuildInputs = [ pkgs.python3Packages.setuptools pkgs.python3Packages.pip ];
      
      propagatedBuildInputs = with pkgs.python3Packages; [ 
        wheel
        discordpy
        colorlog
      ];
      
      format = "setuptools";
      
      doCheck = false;
      
      meta = with pkgs.lib; {
        description = "A Python script to export freelancer data.";
        license = licenses.mit;
      };
    };

    apps.default = {
      type = "app";
      program = "${self.packages.${system}.default}/bin/freelancer_export_script";
    };

    devShells.default = pkgs.mkShell {
      packages = with pkgs; [
    python313
    python313Packages.pip
    python313Packages.setuptools
    python313Packages.wheel
    python313Packages.discordpy
    python313Packages.colorlog
      ];

      shellHook = ''
        echo "Development environment activated..."
        python3 -m pip install -e . --no-build-isolation
      '';
    };
  });
}
