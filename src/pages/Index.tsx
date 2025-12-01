import Hero from "@/components/Hero";
import SoilHealthReport from "@/components/SoilHealthReport";
import CropRecommendation from "@/components/CropRecommendation";
import ChatbotWidget from "@/components/ChatbotWidget";
import SubsidyInfo from "@/components/SubsidyInfo";

const Index = () => {
  return (
    <main className="min-h-screen">
      <Hero />
      <SoilHealthReport />
      <CropRecommendation />
      <ChatbotWidget />
      <SubsidyInfo />
    </main>
  );
};

export default Index;