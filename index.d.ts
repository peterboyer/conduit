declare module "three/addons/loaders/GLTFLoader" {
  export type GLTF = any;
  export class GLTFLoader {
    load(url: string, callback: (gltf: GLTF) => void): void;
  }
}

declare module "three/addons/controls/OrbitControls" {
  import { Camera } from "three";

  export class OrbitControls {
    constructor(camera: Camera, canvas: Element);
    update(): void;
  }
}

declare module "*.gltf?url" {
  const path: string;
  export default path;
}
