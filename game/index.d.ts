declare module "three/addons/loaders/GLTFLoader" {
	import { LoadingManager, Camera } from "three";

	export type GLTF = {
		cameras: Camera[];
	};

	export class GLTFLoader {
		constructor(manager?: LoadingManager);
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
