declare module "three/addons/loaders/GLTFLoader" {
	import type * as THREE from "three";

	export type GLTF = {
		cameras: unknown[];
		scene: THREE.Scene;
	};

	export class GLTFLoader {
		constructor(manager?: THREE.LoadingManager);
		load(url: string, callback: (gltf: GLTF) => void): void;
	}
}

declare module "three/addons/controls/OrbitControls" {
	import type * as THREE from "three";

	export class OrbitControls {
		constructor(camera: THREE.Camera, canvas: Element);
		update(): void;
	}
}

declare module "*.gltf?url" {
	const path: string;
	export default path;
}
