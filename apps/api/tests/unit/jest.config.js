module.exports = {
  preset: 'ts-jest',
  testEnvironment: 'node',
  roots: ['<rootDir>/../src', '<rootDir>'],
  testMatch: ['**/*.test.ts'],
  moduleNameMapper: {
    '^@singularity/shared(.*)$': '<rootDir>/../../packages/shared/src$1'
  },
  collectCoverageFrom: [
    'src/**/*.ts',
    '!src/**/*.test.ts'
  ]
};
