from optimizer import genetic
import feedback

if __name__ == "__main__":
    feedback,feedback_znk = feedback.create_loop()

    print("raw optimization running...")
    genetic.genetic(feedback.f, feedback.acturator.read().tolist(),
            feedback.acturator.min.tolist(), feedback.acturator.max.tolist(),
            goal=80000, initial_trubulance=0.10)
