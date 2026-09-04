package com.ttulka.ecommerce.sales.order.rest;

public class FaultInjection {

    private boolean latencyEnabled = false;

    public void apply() {
        if (!latencyEnabled) {
            return;
        }

        try {
            Thread.sleep(2000);
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        }
    }

    public void enableLatency() {
        latencyEnabled = true;
    }

    public void disableLatency() {
        latencyEnabled = false;
    }

    public boolean isLatencyEnabled() {
        return latencyEnabled;
    }
}