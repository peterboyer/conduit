import { defineConfig } from "vite";

export default defineConfig({
	optimizeDeps: {
		// @workaround
		// Fixes 404 error for loading GET [..]/node_modules/.vite/deps/HavokPhysics.wasm
		// https://forum.babylonjs.com/t/unable-to-load-havok-plugin-error-while-loading-wasm-file-from-browser/40289/27
		exclude: ["@babylonjs/havok"],
	},
});
