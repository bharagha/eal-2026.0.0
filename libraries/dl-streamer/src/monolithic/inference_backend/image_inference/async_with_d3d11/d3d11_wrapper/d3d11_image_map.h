/*******************************************************************************
 * Copyright (C) 2025 Intel Corporation
 *
 * SPDX-License-Identifier: MIT
 ******************************************************************************/

#pragma once

#include "d3d11_images.h"
#include <d3d11.h>
#include <wrl/client.h>


#include "inference_backend/image.h"

namespace InferenceBackend {

class D3D11ImageMap_SystemMemory : public ImageMap {
  public:
    D3D11ImageMap_SystemMemory();
    ~D3D11ImageMap_SystemMemory();

    Image Map(const Image &image) override;
    void Unmap() override;

  protected:
    Microsoft::WRL::ComPtr<ID3D11DeviceContext> d3d11_device_context;
    Microsoft::WRL::ComPtr<ID3D11Texture2D> d3d11_texture;
    int num_planes;
};

class D3D11ImageMap_D3D11Texture : public ImageMap {
  public:
    D3D11ImageMap_D3D11Texture();
    ~D3D11ImageMap_D3D11Texture();

    Image Map(const Image &image) override;
    void Unmap() override;
};

} // namespace InferenceBackend
