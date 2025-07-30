import { defineConfig, loadEnv } from 'vite'
import vue from '@vitejs/plugin-vue'
import process from 'process'
import path from 'path'

export default defineConfig(({mode}) => {
  const env = loadEnv(mode, process.cwd())

  return defineConfig({
    plugins: [vue()],
    resolve: {
      alias: {'@': path.resolve(__dirname, '/src')}
    },
    define: {
      __API_URL__: JSON.stringify(env.VITE_API_URL)
    }
  })
})