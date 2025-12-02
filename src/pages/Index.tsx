import Navbar from "@/components/Navbar";
import Hero from "@/components/Hero";
import SoilHealthReport from "@/components/SoilHealthReport";
import CropRecommendation from "@/components/CropRecommendation";
import HardwareModule from "@/components/HardwareModule";
import ChatbotWidget from "@/components/ChatbotWidget";
import SubsidyInfo from "@/components/SubsidyInfo";

const Index = () => {
  return (
    <main className="min-h-screen">
      <Navbar />
      <div className="pt-16">
        <Hero />
        <SoilHealthReport />
        <CropRecommendation />
        <HardwareModule />
        <ChatbotWidget />
        <SubsidyInfo />
      </div>
    </main>
  );
};

export default Index;