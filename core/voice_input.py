import speech_recognition as sr

MIC_INDEX = 1

def listen_once(timeout: int = 15) -> str:
    r = sr.Recognizer()
    r.energy_threshold        = 200
    r.dynamic_energy_threshold = True
    r.pause_threshold          = 5.0
    r.phrase_threshold         = 0.3
    r.non_speaking_duration    = 4.0

    try:
        with sr.Microphone(device_index=MIC_INDEX) as source:
            r.adjust_for_ambient_noise(source, duration=1)
            audio = r.listen(
                source,
                timeout=timeout,
                phrase_time_limit=60
            )

        try:
            text = r.recognize_google(audio, language="hi-IN")
            return text
        except Exception:
            pass

        try:
            text = r.recognize_google(audio, language="en-IN")
            return text
        except Exception:
            pass

        return ""

    except sr.WaitTimeoutError:
        return ""
    except sr.UnknownValueError:
        return ""
    except Exception:
        return ""

def test_voice():
    result = listen_once(timeout=15)
    if result:
        return result
    return ""

if __name__ == "__main__":
    result = test_voice()
    if result:
        print(f"Suna: {result}")
    else:
        print("Kuch nahi suna")