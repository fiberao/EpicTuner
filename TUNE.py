from optimizer import genetic
import feedback

if __name__ == "__main__":
    feedback_raw,feedback_znk = feedback.create_loop()
    if input("znk/raw?:").find("znk")>=0:
        feedback = feedback_znk
        print("znk optimization running...")
    else:
        print("raw optimization running...")
        feedback = feedback_raw
    genetic.genetic(feedback.f, feedback.acturator.read().tolist(),
            feedback.acturator.min.tolist(), feedback.acturator.max.tolist(),
            goal=80000, initial_trubulance=0.10)
