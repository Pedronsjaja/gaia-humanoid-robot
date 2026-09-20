#include <Arduino.h>
#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>

#ifndef OLED_HEIGHT
#define OLED_HEIGHT 64
#endif
static_assert(OLED_HEIGHT == 32 || OLED_HEIGHT == 64, "Use OLED_HEIGHT 32 or 64");

constexpr uint32_t debounceMs = 25;
struct Button {
  const char *name;
  uint8_t pin;
  bool raw = false;
  bool pressed = false;
  uint32_t changedAt = 0;
  Button(const char *label, uint8_t gpio) : name(label), pin(gpio) {}
};
Button buttons[] = {
    {"UP", 4}, {"DWN", 5}, {"LFT", 6}, {"RHT", 7},
    {"MID", 15}, {"SET", 16}, {"RST", 17},
};
Adafruit_SSD1306 display(128, OLED_HEIGHT, &Wire, -1);
bool displayReady = false;
uint8_t displayAddress = 0;
uint32_t lastStatus = 0;

void printStatus() {
  Serial.print("ESTADO: ");
  for (const auto &button : buttons) {
    Serial.printf("%s=%d ", button.name, button.pressed ? 0 : 1);
  }
  Serial.printf("| OLED=%s", displayReady ? "inicializado" : "indisponivel");
  if (displayAddress) Serial.printf(" (0x%02X)", displayAddress);
  Serial.println(" | 0=pressionado, 1=solto");
}

void drawStatus() {
  if (!displayReady) return;
  display.clearDisplay();
  display.setTextSize(1);
  display.setTextColor(SSD1306_WHITE);
  display.setCursor(0, 0);
  display.print("ESP TOOL - TESTE");
  display.setCursor(0, 8);
  display.print("0=pressionado 1=solto");
  for (size_t i = 0; i < 7; ++i) {
    display.setCursor((i % 4) * 32, 16 + (i / 4) * 8);
    display.printf("%s%d", buttons[i].name, buttons[i].pressed ? 0 : 1);
  }
  if (OLED_HEIGHT == 64) {
    display.setCursor(0, 40);
    display.printf("OLED I2C: 0x%02X", displayAddress);
    display.setCursor(0, 56);
    display.print("Acione cada contato");
  }
  display.display();
}

void setup() {
  Serial.begin(115200);
  // Bounded wait: the display and buttons also work without a serial monitor.
  const uint32_t start = millis();
  while (!Serial && millis() - start < 1500) delay(10);
  Serial.println("\nESP TOOL - diagnostico do joystick e OLED");
  for (auto &button : buttons) {
    pinMode(button.pin, INPUT_PULLUP);
    button.raw = button.pressed = digitalRead(button.pin) == LOW;
    button.changedAt = millis();
    Serial.printf("%s -> GPIO %u\n", button.name, button.pin);
  }

  Wire.begin(8, 9);
  Wire.setClock(100000);
  Wire.setTimeOut(20);
  Serial.println("Varredura I2C: SDA=8, SCL=9");
  for (uint8_t address = 1; address < 127; ++address) {
    Wire.beginTransmission(address);
    if (Wire.endTransmission() == 0) {
      Serial.printf("I2C encontrado: 0x%02X\n", address);
      if (address == 0x3C || (address == 0x3D && displayAddress == 0)) {
        displayAddress = address;
      }
    }
  }
  // An I2C acknowledgement does not identify the controller: SSD1306 is assumed.
  if (displayAddress) {
    displayReady = display.begin(SSD1306_SWITCHCAPVCC, displayAddress, false, false);
  }
  if (!displayReady) {
    Serial.println("OLED indisponivel. Confira VCC/GND, SDA/SCL e modelo.");
    Serial.println("O teste dos botoes continua pela serial.");
  }
  printStatus();
  drawStatus();
  lastStatus = millis();
}

void loop() {
  const uint32_t now = millis();
  bool changed = false;
  for (auto &button : buttons) {
    const bool raw = digitalRead(button.pin) == LOW;
    if (raw != button.raw) {
      button.raw = raw;
      button.changedAt = now;
    }
    if (button.pressed != button.raw && now - button.changedAt >= debounceMs) {
      button.pressed = button.raw;
      Serial.printf("%s GPIO %u: %s\n", button.name, button.pin,
                    button.pressed ? "PRESSIONADO (0)" : "SOLTO (1)");
      changed = true;
    }
  }
  // Periodic status is visible even if the monitor missed the startup messages.
  if (changed || now - lastStatus >= 2000) {
    printStatus();
    drawStatus();
    lastStatus = now;
  }
  delay(1);
}
