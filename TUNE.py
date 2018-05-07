from optimizer import genetic,nm
import feedback
        

if __name__ == "__main__":
    feedback_raw,feedback_znk = feedback.create_loop()
    if input("znk/raw?:").find("znk")>=0:
        feedback = feedback_znk
        print("znk optimization running...")
    else:
        print("raw optimization running...")
        feedback = feedback_raw
    if input("ga/nm?:").find("ga")>=0:
        print("optimization started with Nelder_mead")
        final = nm.nelder_mead(feedback.f, feedback.acturator.read(), max_iter=10000)
        feedback.f(final[0])
    else:
        initial_trubulance=float(input("initial_trubulance(0.1):"))
        print("optimization started with Genetic algorithm")
        genetic.genetic(feedback.f, feedback.acturator.read().tolist(),
                feedback.acturator.min.tolist(), feedback.acturator.max.tolist(),
                goal=80000, initial_trubulance=initial_trubulance)
