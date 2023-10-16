import { GLTF, GLTFLoader } from "three/addons/loaders/GLTFLoader";
import { manager } from "./manager";

import levelUrl from "./level.gltf?url";
import cubeUrl from "./cube.gltf?url";
import carUrl from "./car.gltf?url";

const loader = new GLTFLoader(manager);

function Scene(url: string): { url: string; gltf: Promise<GLTF> } {
	return {
		url: url,
		gltf: new Promise((resolve) => loader.load(url, resolve)),
	};
}

export const level = Scene(levelUrl);
export const cube = Scene(cubeUrl);
export const car = Scene(carUrl);
