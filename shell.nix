{ pkgs ? import <nixpkgs> {} }:

pkgs.mkShellNoCC {
  packages = with pkgs; [
    git
    curl
    python314
    python314Packages.pywebview
    python314Packages.requests
  ];
}
