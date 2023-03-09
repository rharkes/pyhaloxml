#!/bin/bash

# ensure rustup and maturin are installed first!

archs=("x86_64-pc-windows-msvc" "x86_64-unknown-linux-gnu")

for arch in ${archs[@]}; do
  rustup target add $arch
  maturin build --release --target $arch
done
