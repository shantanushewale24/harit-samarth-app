import { useLanguage } from '@/contexts/LanguageContext';
import { getTranslation } from '@/lib/translations';

export const useTranslation = () => {
  const { language } = useLanguage();
  
  const t = (key: string): string => {
    return getTranslation(key, language);
  };

  return { t, language };
};
