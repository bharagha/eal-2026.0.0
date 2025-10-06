/*******************************************************************************
 * Copyright (C) 2025 Intel Corporation
 *
 * SPDX-License-Identifier: MIT
 ******************************************************************************/

#include "d3d11_image_map.h"

#include "inference_backend/logger.h"

using namespace InferenceBackend;

ImageMap *ImageMap::Create(MemoryType type) {
    ImageMap *map = nullptr;
    switch (type) {
    case MemoryType::SYSTEM:
        map = new D3D11ImageMap_SystemMemory();
        break;
    case MemoryType::D3D11:
        map = new D3D11ImageMap_D3D11Texture();
        break;
    default:
        throw std::invalid_argument("Unsupported format for ImageMap");
    }
    return map;
}

D3D11ImageMap_SystemMemory::D3D11ImageMap_SystemMemory(){
}

D3D11ImageMap_SystemMemory::~D3D11ImageMap_SystemMemory() {
    Unmap();
}
Image D3D11ImageMap_SystemMemory::Map(const Image &image) {
    Image image_sys = Image();
    image_sys.type = MemoryType::SYSTEM;
    image_sys.width = image.width;
    image_sys.height = image.height;
    image_sys.format = image.format;

    // Get device context
    static_cast<ID3D11Device*>(image.d3d11_device)->GetImmediateContext(&d3d11_device_context);

    d3d11_texture = static_cast<ID3D11Texture2D*>(image.d3d11_texture);
    D3D11_TEXTURE2D_DESC desc;
    d3d11_texture->GetDesc(&desc);

    num_planes = 1;
    if (desc.Format == DXGI_FORMAT_NV12) {
        num_planes = 2;
    }

    for (int plane = 0; plane < num_planes; ++plane) {
        D3D11_MAPPED_SUBRESOURCE mapped_resource = {};
        HRESULT hr = d3d11_device_context->Map(
            d3d11_texture.Get(),
            plane,
            D3D11_MAP_READ,
            0,
            &mapped_resource
        );
        if (FAILED(hr)) {
            throw std::runtime_error("Failed to map D3D11 texture subresource to system memory");
        }
        image_sys.planes[plane] = static_cast<uint8_t*>(mapped_resource.pData);
        image_sys.stride[plane] = mapped_resource.RowPitch;
    }

    return image_sys;
}

void D3D11ImageMap_SystemMemory::Unmap() {
    for (int plane = 0; plane < num_planes; ++plane) {
        d3d11_device_context->Unmap(
            d3d11_texture.Get(),
            plane
        );
    }
}

D3D11ImageMap_D3D11Texture::D3D11ImageMap_D3D11Texture() {
}

D3D11ImageMap_D3D11Texture::~D3D11ImageMap_D3D11Texture() {
    Unmap();
}

Image D3D11ImageMap_D3D11Texture::Map(const Image &image) {
    return image;
}

void D3D11ImageMap_D3D11Texture::Unmap() {
}
