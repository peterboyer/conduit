import * as THREE from "three";
import { GLTFLoader } from "three/addons/loaders/GLTFLoader";
import { OrbitControls } from "three/addons/controls/OrbitControls";
import sceneGltf from "./scene.gltf?url";

{
  // const fov = 45;
  // const aspect = window.innerWidth / window.innerHeight;
  // const near = 0.01;
  // const far = 10;
  // const camera = new THREE.PerspectiveCamera(fov, aspect, near, far);
}

const scene = new THREE.Scene();
scene.background = new THREE.Color("grey");

// {
//   const skyColor = 0xb1e1ff; // light blue
//   const groundColor = 0xb97a20; // brownish orange
//   const intensity = 2;
//   const light = new THREE.HemisphereLight(skyColor, groundColor, intensity);
//   scene.add(light);
// }

const canvas = document.querySelector("#app")!;

let camera = new THREE.PerspectiveCamera();

const url = sceneGltf;
const gltfLoader = new GLTFLoader();
gltfLoader.load(url, (gltf) => {
  console.log(gltf);
  const root = gltf.scene;
  camera = gltf.cameras[0];
  const controls = new OrbitControls(camera, canvas);
  controls.update();
  scene.add(root);
});

const renderer = new THREE.WebGLRenderer({ antialias: true, canvas });
renderer.setSize(window.innerWidth, window.innerHeight);
renderer.setAnimationLoop(animation);

function animation(_dt: number) {
  renderer.render(scene, camera);
}
