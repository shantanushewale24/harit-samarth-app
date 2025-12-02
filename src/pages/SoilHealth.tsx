import Navbar from "@/components/Navbar";
import SoilHealthReport from "@/components/SoilHealthReport";
import ChatbotWidget from "@/components/ChatbotWidget";

const SoilHealth = () => {
  return (
    <main className="min-h-screen">
      <Navbar />
      <div className="pt-16">
        <SoilHealthReport />
        <ChatbotWidget />
      </div>
    </main>
  );
};

export default SoilHealth;
