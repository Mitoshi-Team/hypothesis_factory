{
  description = "ML Worker DevShell";

  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs?ref=nixos-unstable";
    flake-parts.url = "github:hercules-ci/flake-parts";
    working-devshells = {
      url = "git+https://git.geekiot.tech/geekiot/working-devshells.git";
      inputs.nixpkgs.follows = "nixpkgs";
    };
  };

  outputs =
    inputs:
    inputs.flake-parts.lib.mkFlake { inherit inputs; } {
      systems = inputs.working-devshells.systems;
      imports = [ inputs.working-devshells.flakeModule ];

      perSystem =
        {
          config,
          pkgs,
          ...
        }:
        let
          nvidiaPackages = [
            "nvidia-cublas"
            # "nvidia-cuda-cupti"
            "nvidia-cuda-nvrtc"
            "nvidia-cuda-runtime"
            "nvidia-cudnn-cu13"
            "nvidia-cufft"
            "nvidia-cufile"
            "nvidia-curand"
            "nvidia-cusolver"
            "nvidia-cusparse"
            "nvidia-cusparselt-cu13"
            "nvidia-nccl-cu13"
            "nvidia-nvjitlink"
            "nvidia-nvshmem-cu13"
            "nvidia-nvtx"
          ];
          binaryPackages = [ "torch" ] ++ nvidiaPackages;
          torchIgnoredLibs = [
            "libcuda.so.1"
            "libcupti.so.13"
            "libcudart.so.13"
            "libnvshmem_host.so.3"
            "libcudnn.so.9"
            "libcufile.so.0"
            "libcusparseLt.so.0"
            "libnccl.so.2"
            "libcurand.so.10"
            "libcublas.so.13"
            "libcublasLt.so.13"
            "libnvrtc.so.13"
            "libcusolver.so.12"
            "libcusparse.so.12"
            "libcufft.so.12"
          ];
        in
        {
          workingDevShells.python = {
            enable = true;
            pythonPackage = pkgs.python313;
            workspaceRoot = ../../.;
            overlays = [
              (
                final: prev:
                let
                  binary-libs = pkgs.runCommand "python-binary-libs" { } ''
                    mkdir -p $out/lib
                    for pkg in ${pkgs.lib.concatStringsSep " " (map (name: final.${name}) binaryPackages)}; do
                      if [ -d "$pkg" ]; then
                        find "$pkg" -name '*.so*' -exec cp -L {} $out/lib/ \;
                      fi
                    done
                  '';
                in
                {
                  torch = prev.torch.overrideAttrs (old: {
                    autoPatchelfIgnoreMissingDeps = (old.autoPatchelfIgnoreMissingDeps or [ ]) ++ torchIgnoredLibs;
                  });
                }
                // (pkgs.lib.genAttrs nvidiaPackages (
                  name:
                  prev.${name}.overrideAttrs (old: {
                    autoPatchelfIgnoreMissingDeps = true;
                  })
                ))
                // {
                  torchaudio = prev.torchaudio.overrideAttrs (old: {
                    buildInputs = (old.buildInputs or [ ]) ++ [ binary-libs ];
                    autoPatchelfSearchPath = (old.autoPatchelfSearchPath or "") + ":${binary-libs}/lib";
                  });

                  torchcodec = prev.torchcodec.overrideAttrs (old: {
                    buildInputs = (old.buildInputs or [ ]) ++ [ binary-libs ];
                    autoPatchelfSearchPath = (old.autoPatchelfSearchPath or "") + ":${binary-libs}/lib";
                    autoPatchelfIgnoreMissingDeps = true;
                  });
                }
              )
            ];
          };

          devShells.default = config.devShells.python.overrideAttrs (old: {
            buildInputs = (old.buildInputs or [ ]) ++ [
              pkgs.libsndfile
              pkgs.ffmpeg
            ];
            shellHook = (old.shellHook or "") + ''
              export LD_LIBRARY_PATH="${pkgs.lib.getLib pkgs.libsndfile}/lib:${pkgs.lib.getLib pkgs.ffmpeg}/lib''${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}"
            '';
          });
        };
    };
}
