package com.ttulka.ecommerce.incident;

import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import lombok.RequiredArgsConstructor;

@RestController
@RequestMapping("/incident/database")
@RequiredArgsConstructor
public class IncidentDatabaseController {

    private final JdbcTemplate jdbcTemplate;

    @GetMapping
    public Map<String, Object> diagnostics() {
        long start = System.nanoTime();

        Integer ordersCount = jdbcTemplate.queryForObject(
                "SELECT COUNT(*) FROM orders",
                Integer.class);

        Integer orderItemsCount = jdbcTemplate.queryForObject(
                "SELECT COUNT(*) FROM order_items",
                Integer.class);

        List<Map<String, Object>> recentOrders = jdbcTemplate.queryForList(
                "SELECT * FROM orders LIMIT 10");

        double latencyMs =
                (System.nanoTime() - start) / 1_000_000.0;

        Map<String, Object> response = new LinkedHashMap<>();

        response.put("database", "H2");
        response.put("status", "HEALTHY");
        response.put("query_latency_ms", Math.round(latencyMs * 100.0) / 100.0);
        response.put("orders_count", ordersCount);
        response.put("order_items_count", orderItemsCount);
        response.put("recent_orders", recentOrders);

        return response;
    }
}