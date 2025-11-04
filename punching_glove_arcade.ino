/*
 * Punch Strength Arcade Machine for Seeed XIAO MG24 Sense
 * Embedded audio version + PAM8302 amplifier + BC547 power control
 */

#include "LSM6DS3.h"
#include "audio_data.h"  // Generated header with embedded audio
#include <math.h>

// === Hardware Configuration ===
#define AUDIO_PIN D0          // PWM pin for audio output
#define AMP_CTRL_PIN D1       // Controls BC547 transistor (ON/OFF)
#define SAMPLE_RATE 8000      // 8kHz sample rate

// IMU instance
LSM6DS3 imu(I2C_MODE, 0x6A);

// === Punch Detection Parameters ===
#define ACCEL_THRESHOLD 2.5   // g-force threshold to detect punch start
#define COOLDOWN_MS 2000      // Minimum time between punches
#define SAMPLE_WINDOW_MS 200  // Window to capture peak acceleration

// === Score Mapping ===
#define MIN_SCORE 100
#define MAX_SCORE 999
#define MIN_GFORCE 2.5
#define MAX_GFORCE 20.0

// State variables
bool punchInProgress = false;
float peakAcceleration = 0.0;
unsigned long punchStartTime = 0;
unsigned long lastPunchTime = 0;

void setup() {
  Serial.begin(115200);
  delay(1000);
  Serial.println("=== Punch Strength Arcade Machine ===");
  Serial.println("(Embedded Audio + PAM8302 + BC547 Control)");

  // Initialize IMU
  if (imu.begin() != 0) {
    Serial.println("ERROR: IMU initialization failed!");
    while (1);
  }
  Serial.println("✓ IMU initialized");

  // Audio PWM setup
  pinMode(AUDIO_PIN, OUTPUT);
  analogWriteResolution(8);
  Serial.println("✓ Audio PWM ready");

  // Amplifier control pin
  pinMode(AMP_CTRL_PIN, OUTPUT);
  digitalWrite(AMP_CTRL_PIN, LOW); // Keep amplifier OFF initially
  Serial.println("✓ Amplifier control ready (BC547 OFF)");

  // Audio data info
  Serial.print("✓ Audio files embedded: ");
  Serial.println(audioFileCount);
  size_t totalSize = 0;
  for (int i = 0; i < audioFileCount; i++) totalSize += audioFiles[i].length;
  Serial.print("Total embedded audio: ");
  Serial.print(totalSize / 1024.0, 1);
  Serial.println(" KB");

  Serial.println("\n🥊 Ready! Punch the glove!\n");
}

void loop() {
  float ax = imu.readFloatAccelX();
  float ay = imu.readFloatAccelY();
  float az = imu.readFloatAccelZ();

  float accelMagnitude = sqrt(ax * ax + ay * ay + az * az);
  unsigned long currentTime = millis();

  if (!punchInProgress) {
    if (accelMagnitude > ACCEL_THRESHOLD &&
        (currentTime - lastPunchTime) > COOLDOWN_MS) {
      punchInProgress = true;
      punchStartTime = currentTime;
      peakAcceleration = accelMagnitude;
      Serial.println(">>> Punch detected! Measuring...");
    }
  } else {
    if (accelMagnitude > peakAcceleration) {
      peakAcceleration = accelMagnitude;
    }

    if (currentTime - punchStartTime > SAMPLE_WINDOW_MS) {
      punchInProgress = false;
      lastPunchTime = currentTime;

      int score = calculateScore(peakAcceleration);
      Serial.print("Peak Acceleration: ");
      Serial.print(peakAcceleration);
      Serial.print(" g  →  Score: ");
      Serial.println(score);

      announceScore(score);

      Serial.println("🥊 Ready for next punch!\n");
    }
  }

  delay(10);
}

// === Score Calculation ===
int calculateScore(float gForce) {
  if (gForce < MIN_GFORCE) gForce = MIN_GFORCE;
  if (gForce > MAX_GFORCE) gForce = MAX_GFORCE;

  float normalized = (gForce - MIN_GFORCE) / (MAX_GFORCE - MIN_GFORCE);
  normalized = pow(normalized, 0.9);

  int score = MIN_SCORE + (int)(normalized * (MAX_SCORE - MIN_SCORE));
  return constrain(score, MIN_SCORE, MAX_SCORE);
}

// === Score Announcement ===
void announceScore(int score) {
  // Turn amplifier ON
  digitalWrite(AMP_CTRL_PIN, HIGH);
  delay(100); // small delay for amp to stabilize

  int hundreds = (score / 100) * 100;
  int remainder = score % 100;
  int tens = (remainder / 10) * 10;
  int ones = remainder % 10;

  Serial.print("🔊 Announcing: ");

  if (hundreds > 0) {
    Serial.print(hundreds); Serial.print(" ");
    playAudioFile(String(hundreds) + ".wav");
  }

  if (remainder > 0) {
    Serial.print("and ");
    playAudioFile("and.wav");
  }

  if (remainder >= 20) {
    Serial.print(tens); Serial.print(" ");
    playAudioFile(String(tens) + ".wav");
    if (ones > 0) {
      Serial.print(ones); Serial.print(" ");
      playAudioFile(String(ones) + ".wav");
    }
  } else if (remainder >= 10) {
    Serial.print(remainder); Serial.print(" ");
    playAudioFile(String(remainder) + ".wav");
  } else if (ones > 0) {
    Serial.print(ones); Serial.print(" ");
    playAudioFile(String(ones) + ".wav");
  }

  Serial.println();

  // Turn amplifier OFF after playback
  delay(200);
  digitalWrite(AMP_CTRL_PIN, LOW);
}

// === Audio File Lookup ===
int findAudioFile(String filename) {
  for (int i = 0; i < audioFileCount; i++) {
    if (strcmp(audioFiles[i].name, filename.c_str()) == 0) {
      return i;
    }
  }
  return -1;
}

// === Audio Playback ===
void playAudioFile(String filename) {
  int fileIndex = findAudioFile(filename);
  if (fileIndex == -1) {
    Serial.print("⚠️ Missing audio: ");
    Serial.println(filename);
    return;
  }

  const AudioFile* audio = &audioFiles[fileIndex];
  uint32_t sampleInterval = 1000000 / SAMPLE_RATE;
  uint32_t nextSample = micros();

  noInterrupts();
  for (uint32_t i = 0; i < audio->length; i++) {
    uint8_t sample = pgm_read_byte(&audio->data[i]);
    analogWrite(AUDIO_PIN, sample);

    nextSample += sampleInterval;
    while ((int32_t)(micros() - nextSample) < 0);
  }
  interrupts();
  delay(80);
}
