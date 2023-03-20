package io.airbyte.integrations.util;

import com.amazonaws.util.IOUtils;
import java.io.Closeable;
import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.RejectedExecutionException;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * CloseableResourceManager is a singleton class that can help keep track of resources that need closing
 * at the completion of a sync. The original target of this is Snowflake destination, but any connector
 * that needs to close a resource on completion of a sync can use this class to track those long running
 * resources and close them at completion of the sync.
 */
public class CloseableResourceManager {

  private static final Logger LOGGER = LoggerFactory.getLogger(CloseableResourceManager.class);
  private static final CloseableResourceManager instance = new CloseableResourceManager();

  private final List<Closeable> resources = new ArrayList<>();
  private volatile boolean running;

  /**
   * Get the singleton instance of this class
   */
  public static CloseableResourceManager getInstance() {
    return instance;
  }

  /**
   * Do not instantiate this class directly.
   */
  private CloseableResourceManager() {
    running = true;
  }

  /**
   * Add a resource to track that needs closing later in the sync process
   * (for example in the onCloseFunction)
   */
  public synchronized void addCloseable(final Closeable closeable) {
    if (!running) {
      throw new RejectedExecutionException("CloseableResouceManager already shut down");
    }
    resources.add(closeable);
  }

  /**
   * Call this method after ALL processing is complete prior to close
   */
  public synchronized void closeAll() {
    running = false;
    resources.forEach(closeable -> IOUtils.closeQuietly(closeable, null));
    resources.clear();
    LOGGER.info("Finished closing long running resources");
  }
}
