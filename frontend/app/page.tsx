import { TopBar } from "@/components/TopBar";
import { AgentStream } from "@/components/AgentStream";
import { ResultsPanel } from "@/components/ResultsPanel";

export default function Home() {
  return (
    <div className="flex flex-col h-screen bg-white dark:bg-[#0f0f1a]">
      <TopBar />
      <main className="flex flex-1 overflow-hidden">
        <section className="flex-1 overflow-hidden border-r border-slate-200 dark:border-slate-800">
          <AgentStream />
        </section>
        <section className="flex-1 overflow-hidden">
          <ResultsPanel />
        </section>
      </main>
    </div>
  );
}
