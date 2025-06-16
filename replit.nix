{ pkgs }: {
  deps = [
    pkgs.python311Full    # Full Python 3.11 environment
    pkgs.libstdcxx       # This adds the missing libstdc++.so.6
  ];
}
