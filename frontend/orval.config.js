module.exports = {
  api: {
    input: {
      target: '../backend/schema.yaml',
    },
    output: {
      mode: 'split',
      target: './src/api/generated.ts',
      schemas: './src/api/schemas',
      client: 'react-query',
      prettier: true,
      override: {
        mutator: {
          path: './src/api/mutator.ts',
          name: 'customInstance',
        },
        query: {
          useQuery: true,
          useInfinite: true,
          useInfiniteQueryParam: 'page',
        },
      },
    },
  },
};
