import babel from 'rollup-plugin-babel';
import cjs from 'rollup-plugin-commonjs';
import replace from 'rollup-plugin-replace';
import resolve from 'rollup-plugin-node-resolve';

export default {
  entry: 'static/js/app/components/init.es6',
  format: 'iife',
  dest: 'static/js/app/bundle.js',
  sourceMap: false,
  globals: {
    'axios': 'axios',
    'classnames': 'classNames',
    'react': 'React',
    'react-dom': 'ReactDOM',
    'react-slick': 'Slider'
  },
  external: ['axios', 'classnames', 'react', 'react-dom', 'react-slick'],
  plugins: [
    babel({
      babelrc: false,
      plugins: [
          "external-helpers",
          "transform-react-jsx"
      ],
      presets: [
        [ "es2015", { "modules": false } ]
      ],
      exclude: 'node_modules/**'
    }),
    resolve({ 
      jsnext: true, 
      main: true 
    }),
    replace({
      'process.env.NODE_ENV': JSON.stringify('development')
    }),
    cjs(),
  ]
};
