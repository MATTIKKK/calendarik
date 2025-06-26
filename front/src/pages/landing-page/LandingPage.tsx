import Hero from '../../components/landing/Hero';
import HowItWorks from '../../components/landing/HowItWorks';
import Features from '../../components/landing/Features';
import PersonalitySelector from '../../components/landing/PersonalitySelector';
import Reviews from '../../components/landing/Reviews';
import Pricing from '../../components/landing/Pricing';
import FAQ from '../../components/landing/FAQ';
import Footer from '../../components/landing/Footer';



const LandingPage = () => {
    return (
        <div className="min-h-screen ">
          <Hero />
          <HowItWorks />
          <Features />
          <PersonalitySelector />
          <Reviews />
          <Pricing />
          <FAQ />
          <Footer />
        </div>
      );
}

export default LandingPage
