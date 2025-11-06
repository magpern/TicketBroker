package com.ticketbroker.service;

import com.ticketbroker.model.Settings;
import com.ticketbroker.repository.SettingsRepository;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.Optional;

@Service
public class SettingsService {
    private final SettingsRepository settingsRepository;
    
    public SettingsService(SettingsRepository settingsRepository) {
        this.settingsRepository = settingsRepository;
    }
    
    public String getValue(String key, String defaultValue) {
        return settingsRepository.findByKey(key)
                .map(Settings::getValue)
                .orElse(defaultValue);
    }
    
    @Transactional
    public Settings setValue(String key, String value) {
        Optional<Settings> existing = settingsRepository.findByKey(key);
        if (existing.isPresent()) {
            Settings setting = existing.get();
            setting.setValue(value);
            return settingsRepository.save(setting);
        } else {
            Settings setting = new Settings();
            setting.setKey(key);
            setting.setValue(value);
            return settingsRepository.save(setting);
        }
    }
    
    public Optional<Settings> getSetting(String key) {
        return settingsRepository.findByKey(key);
    }
}

