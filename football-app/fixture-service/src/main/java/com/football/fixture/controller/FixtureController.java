package com.football.fixture.controller;

import com.football.fixture.model.Fixture;
import com.football.fixture.repository.FixtureRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/fixtures")
@RequiredArgsConstructor
public class FixtureController {

    private final FixtureRepository repository;

    @GetMapping
    public List<Fixture> getAllFixtures() {
        return repository.findAll();
    }

    @GetMapping("/upcoming")
    public List<Fixture> getUpcomingFixtures() {
        return repository.findByStatus("SCHEDULED");
    }

    @PostMapping
    public Fixture createFixture(@RequestBody Fixture fixture) {
        return repository.save(fixture);
    }
}
