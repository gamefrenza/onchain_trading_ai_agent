import '@testing-library/jest-dom';

declare global {
    namespace NodeJS {
        interface Global {
            fetch: jest.Mock;
        }
    }
}

(global as any).fetch = jest.fn(); 