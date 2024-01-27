{ pkgs }: {
  deps = [
    pkgs.sqlite.bin
    pkgs.sqlite-interactive.bin
  ];
}