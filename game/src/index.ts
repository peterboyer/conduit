import HavokPhysics from "@babylonjs/havok";
import {
	Vector3,
	Engine,
	Scene,
	SceneLoader,
	HemisphericLight,
	ArcRotateCamera,
	Color3,
	Color4,
	AssetContainer,
	InstantiatedEntries,
	HavokPlugin,
	Mesh,
	PhysicsAggregate,
	PhysicsShapeType,
	HingeConstraint,
} from "@babylonjs/core";
import "@babylonjs/loaders/glTF";

import levelUrl from "./scenes/level.glb?url";
import cubeUrl from "./scenes/cube.glb?url";
import carUrl from "./scenes/car.glb?url";
import { Inspector } from "@babylonjs/inspector";

(async () => {
	const canvas = document.getElementById("app") as HTMLCanvasElement;

	const antialias = true;
	const engine = new Engine(canvas, antialias);

	const scene = new Scene(engine);
	scene.clearColor = Color4.FromColor3(Color3.Gray());

	{
		const havok = await HavokPhysics();
		const gravity = new Vector3(0, -9.81, 0);
		const plugin = new HavokPlugin(true, havok);
		scene.enablePhysics(gravity, plugin);
	}

	const physicsHelper = false;

	Inspector.Show(scene, {});
	if (physicsHelper) {
		// @workaround
		// Turn on Physics Helper
		// @ts-ignore
		document.querySelector('.label[title="Debug"]')!.click();
		setTimeout(() => {
			// @ts-ignore
			document.querySelectorAll(".container.lbl")[1]!.click();
		}, 200);
	}

	function load(url: string) {
		return new Promise<AssetContainer>((resolve) => {
			const rootUrl = url;
			const sceneFilename = undefined;
			SceneLoader.LoadAssetContainer(rootUrl, sceneFilename, scene, resolve);
		});
	}

	const level = await load(levelUrl);
	const cube = await load(cubeUrl);
	const car = await load(carUrl);

	console.log(scene);
	console.log({ level, cube, car });

	level.addToScene();
	const aggregates: PhysicsAggregate[] = [];

	const actors: Record<
		"cube" | "car",
		{ entries: InstantiatedEntries; aggregates: PhysicsAggregate[] }[]
	> = {
		cube: [],
		car: [],
	};
	const nodes = scene.getNodes();
	nodes.forEach((node) => {
		const actorTypeUnsafe = node.metadata?.gltf?.extras?.conduit_actor as
			| string
			| undefined;

		if (!actorTypeUnsafe) {
			if (node instanceof Mesh && node.geometry) {
				const mesh = node;
				const aggregate = new PhysicsAggregate(
					mesh,
					PhysicsShapeType.MESH,
					{ mass: 0 },
					scene,
				);
				aggregates.push(aggregate);
			}

			return;
		}

		if (actorTypeUnsafe === "cube") {
			const entries = cube.instantiateModelsToScene();
			const aggregates: PhysicsAggregate[] = [];
			entries.rootNodes.forEach((rootNode) => {
				rootNode.parent = node;
				rootNode.getChildMeshes().forEach((mesh) => {
					const aggregate = new PhysicsAggregate(
						mesh,
						PhysicsShapeType.MESH,
						{ mass: 10 },
						scene,
					);
					aggregates.push(aggregate);
				});
			});
			actors.cube.push({ entries, aggregates });
		} else if (actorTypeUnsafe === "car") {
			const entries = car.instantiateModelsToScene(
				(name) => `car[${actors.car.length}].${name}`,
			);
			const aggregates: PhysicsAggregate[] = [];
			entries.rootNodes.forEach((rootNode) => {
				const _car: Partial<Record<string, PhysicsAggregate>> = {};
				rootNode.parent = node;
				rootNode.getChildren().forEach((node) => {
					if (!(node instanceof Mesh)) {
						return;
					}
					const mesh = node;
					mesh.visibility = 0;
					const aggregate = new PhysicsAggregate(
						mesh,
						PhysicsShapeType.MESH,
						{ mass: 10 },
						scene,
					);
					_car["body"] = aggregate;
					aggregates.push(aggregate);
				});
				rootNode.getChildMeshes().forEach((mesh) => {
					console.log({ mesh }, mesh.name);
					const id = mesh.name.split(".")[1];
					if (!id?.startsWith("w_")) {
						return;
					}

					const aggregate = new PhysicsAggregate(
						mesh,
						PhysicsShapeType.MESH,
						{ mass: 10 },
						scene,
					);
					_car[id] = aggregate;
					aggregates.push(aggregate);
				});

				const car_body = _car["body"];
				const car_w_fl = _car["w_fl"];
				const car_w_fr = _car["w_fr"];
				const car_w_rl = _car["w_rl"];
				const car_w_rr = _car["w_rr"];

				if (!(car_body && car_w_fl && car_w_fr && car_w_rl && car_w_rr)) {
					throw new Error("bad car asset, missing body and/or wheels (w_*)");
				}

				// https://dzone.com/articles/webgl-physics-based-car-using-babylonjs-and-oimojs
				const constraint = new HingeConstraint(
					new Vector3(),
					new Vector3(),
					new Vector3(),
					new Vector3(),
					scene,
				);
				car_body.body.addConstraint(car_w_fl.body, constraint);
				car_body.body.addConstraint(car_w_fr.body, constraint);
				car_body.body.addConstraint(car_w_rl.body, constraint);
				car_body.body.addConstraint(car_w_rr.body, constraint);
			});
			actors.car.push({ entries, aggregates });
		}
	});

	const camera = new ArcRotateCamera(
		"camera",
		-Math.PI / 2,
		Math.PI / 2.5,
		40,
		new Vector3(0, 0, 0),
		scene,
	);
	camera.attachControl(canvas, true);

	const light = new HemisphericLight("light1", new Vector3(0, 1, 0), scene);
	light.intensity = 0.7;

	engine.runRenderLoop(() => {
		scene.render();
	});
})();
