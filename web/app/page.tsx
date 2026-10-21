import { Defs } from "@/components/landing/Defs";
import { Motion } from "@/components/landing/Motion";
import { Bar, Loader, Hero, Manifesto, Act, Ensemble, Finale, Footer } from "@/components/landing/Sections";
import { ChatBox, ResumeBox, TheoryBox, DsaBox, DashBox } from "@/components/landing/boxes/Boxes";

export default function Home() {
  return (
    <>
      <Defs />
      <a className="skip" href="#main">
        Skip to content
      </a>
      <Motion>
        <Loader />
        <Bar />
        <main id="main">
          <Hero />
          <Manifesto />

          <Act
            id="act1"
            tone="yellow"
            label="Act 1 · Prepare"
            n={1}
            title="Prepare"
            image={{ src: "/images/pages.webp", width: 910, height: 1422, alt: "Performer in a costume of stacked white pages, holding out a blank panel" }}
            steps={[
              { word: "Add the JD", cap: "Paste it or upload it." },
              { word: "Add your resume", cap: "PDF, any version." },
              { word: "Ask anything", cap: "Every answer cites its page." },
            ]}
            statement="Your documents do the talking."
          >
            <ChatBox />
            <ResumeBox />
          </Act>

          <Act
            id="act2"
            tone="rose"
            label="Act 2 · Practise"
            n={2}
            title="Practise"
            image={{ src: "/images/pair.webp", width: 1169, height: 1199, alt: "Two costumed performers facing each other: one leaning in to ask, one standing still to listen" }}
            steps={[
              { word: "Get asked", cap: "Questions from your own material." },
              { word: "Get scored", cap: "Strengths and gaps, out of 10." },
              { word: "Face follow-ups", cap: "Up to three, on what stayed vague." },
            ]}
            statement="Answer. Get scored. Get pushed."
          >
            <TheoryBox />
          </Act>

          <Act
            id="act3"
            tone="black"
            label="Act 3 · Prove"
            n={3}
            title="Prove"
            image={{ src: "/images/rings.webp", width: 550, height: 1425, alt: "Performer in a target-ring costume standing on a three-step pedestal" }}
            steps={[
              { word: "Solve real code", cap: "Real LeetCode problems." },
              { word: "Get reviewed", cap: "Correctness and complexity." },
              { word: "See your score", cap: "One readiness number." },
            ]}
            statement="Real code. One score."
          >
            <DsaBox />
            <DashBox />
          </Act>

          <Ensemble />
          <Finale />
        </main>
        <Footer />
      </Motion>
    </>
  );
}
