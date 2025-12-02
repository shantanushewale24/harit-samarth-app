import { Button } from "@/components/ui/button";
import { Sprout, MessageSquare } from "lucide-react";
import heroImage from "@/assets/hero-farmland.jpg";
import { useTranslation } from "@/hooks/useTranslation";

const Hero = () => {
  const { t } = useTranslation();

  return (
    <section id="home" className="relative min-h-[600px] flex items-center justify-center overflow-hidden">
      <div 
        className="absolute inset-0 bg-cover bg-center"
        style={{ backgroundImage: `url(${heroImage})` }}
      >
        <div className="absolute inset-0 bg-gradient-to-r from-primary/90 via-primary/70 to-transparent" />
      </div>
      
      <div className="container relative z-10 mx-auto px-4 py-20">
        <div className="max-w-2xl">
          <h1 className="text-5xl md:text-6xl font-bold text-white mb-6 animate-in fade-in slide-in-from-bottom-4 duration-1000">
            Agri bio
          </h1>
          <p className="text-xl md:text-2xl text-white/95 mb-4 animate-in fade-in slide-in-from-bottom-4 duration-1000 delay-100">
            {t('hero.title')}
          </p>
          <p className="text-lg text-white/90 mb-8 animate-in fade-in slide-in-from-bottom-4 duration-1000 delay-200">
            {t('hero.subtitle')}
          </p>
          
          <div className="flex flex-wrap gap-4 animate-in fade-in slide-in-from-bottom-4 duration-1000 delay-300">
            <Button size="lg" variant="default" className="bg-harvest text-harvest-foreground hover:bg-harvest/90 shadow-strong">
              <Sprout className="mr-2 h-5 w-5" />
              {t('hero.cta')}
            </Button>
            <Button size="lg" variant="outline" className="bg-white/10 text-white border-white/30 hover:bg-white/20 backdrop-blur-sm">
              <MessageSquare className="mr-2 h-5 w-5" />
              {t('hero.subtitle')}
            </Button>
          </div>
        </div>
      </div>
      
      <div className="absolute bottom-8 left-1/2 -translate-x-1/2 animate-bounce">
        <div className="w-6 h-10 border-2 border-white/50 rounded-full flex items-start justify-center p-2">
          <div className="w-1 h-3 bg-white/70 rounded-full" />
        </div>
      </div>
    </section>
  );
};

export default Hero;