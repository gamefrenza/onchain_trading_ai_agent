interface RetryOptions {
  retries: number;
  delay: number;
}

export async function retry<T>(
  fn: () => Promise<T>,
  options: RetryOptions
): Promise<T> {
  try {
    return await fn();
  } catch (error) {
    if (options.retries === 0) {
      throw error;
    }
    
    await new Promise(resolve => setTimeout(resolve, options.delay));
    
    return retry(fn, {
      retries: options.retries - 1,
      delay: options.delay,
    });
  }
} 