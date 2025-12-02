import Navbar from "@/components/Navbar";
import HardwareModule from "@/components/HardwareModule";
import ChatbotWidget from "@/components/ChatbotWidget";

const Hardware = () => {
  return (
    <main className="min-h-screen">
      <Navbar />
      <div className="pt-16">
        <HardwareModule />
        <ChatbotWidget />
      </div>
    </main>
  );
};

export default Hardware;
