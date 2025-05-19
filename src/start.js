import React, { useState, useRef, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import hero_1 from './images/frontpage/hero_1.svg';
import hero_2 from './images/frontpage/hero_2.png';
import intro_image_1 from './images/frontpage/intro_1.svg';
import intro_image_1_small from './images/frontpage/intro_1_small.svg';
import intro_image_2 from './images/frontpage/secure_ip.jpg';
import Redis from './images/audits/redis_logo.png';
import FastAPI from './images/audits/fastapi_logo.png';
import Axios from './images/audits/axios_logo.png';
import icon_1 from './images/frontpage/icon_1.svg';
import icon_2 from './images/frontpage/icon_2.svg';
import icon_3 from './images/frontpage/icon_3.svg';
import icon_4 from './images/frontpage/icon_4.svg';
import HeroCard3D from './landingpage/start/components/HeroCard3D';
import './Start.css';

const BenefitCard = ({ icon, title, description }) => (
  <div className="benefit-card">
    <img src={icon} alt="" className="benefit-icon" loading="lazy" />
    <h3>{title}</h3>
    <p>{description}</p>
  </div>
);

const BenefitCards = () => {
  const benefits = [
    {
      icon: icon_1,
      title: "Simplify your technical due diligence",
      description: "Streamline your technical assessment process with automated analysis and clear, actionable insights."
    },
    {
      icon: icon_2,
      title: "Get full-spectrum analysis",
      description: "From code quality to security vulnerabilities, get comprehensive insights into your technical investments."
    },
    {
      icon: icon_3,
      title: "Improve your investment thesis",
      description: "Make data-driven decisions with detailed technical metrics and performance indicators."
    },
    {
      icon: icon_4,
      title: "Reduce investment risk",
      description: "Identify potential technical risks early and ensure sustainable technology investments."
    }
  ];

  return (
    <div className="benefits-section">
      <div className="benefits-grid">
        {benefits.map((benefit, index) => (
          <BenefitCard
            key={index}
            icon={benefit.icon}
            title={benefit.title}
            description={benefit.description}
          />
        ))}
      </div>
    </div>
  );
};

const IntroBlock = () => {
  const [currentIntroImage, setCurrentIntroImage] = useState(intro_image_1);
  const section2Ref = useRef(null);

  useEffect(() => {
    const handleResize = () => {
      setCurrentIntroImage(window.innerWidth < 1000 ? intro_image_1_small : intro_image_1);
    };

    // Set initial image
    handleResize();

    // Add event listener
    window.addEventListener('resize', handleResize);

    // Cleanup
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  useEffect(() => {
    const handleParallax = () => {
      if (!section2Ref.current) return;

      const section = section2Ref.current;
      const rect = section.getBoundingClientRect();
      const viewportHeight = window.innerHeight;
      
      // Calculate how far the section is from the top of the viewport
      const sectionTop = rect.top;
      const sectionHeight = rect.height;
      
      // Calculate the percentage of the section that has been scrolled
      // This will give us a value between -1 and 1
      const scrollProgress = (viewportHeight - sectionTop) / (viewportHeight + sectionHeight) * 0.5;
      
      // Calculate parallax offset (adjust multiplier to control effect intensity)
      const maxOffset = 200;
      const offset = maxOffset * scrollProgress;

      // Apply the transform when the section is near or in the viewport
      if (rect.top < viewportHeight + 200 && rect.bottom > -200) {
        requestAnimationFrame(() => {
          section.style.setProperty('--parallax-offset', `${offset}px`);
        });
      }
    };

    window.addEventListener('scroll', handleParallax, { passive: true });
    handleParallax(); // Initial position

    return () => window.removeEventListener('scroll', handleParallax);
  }, []);

  const navigate = useNavigate();

  return (
    <div className="intro-block">
      <BenefitCards />
      <div className="intro-section intro-section-2" ref={section2Ref}>
        <div className="intro-image-column">
          <img src={intro_image_2} alt="IP protection visualization" loading="lazy"/>
        </div>
        <div className="intro-text-column">
          <h2>Transparent Insights, Protected Intellectual Property</h2>
          <p>Built to protect the core of software - the code - without limiting actionable insights into its quality. 
            No single line of code is ever disclosed.
          </p>
          <button className="intro-cta-button" onClick={() => navigate('/security')}>Read about security</button>
        </div>
      </div>
    </div>
  );
};

const FeatureSection = () => {
  const [activeFeature, setActiveFeature] = useState('easy');

  const featureContent = {
    easy: {
      title: "Technical due diligence has never been this easy.",
      features: [
        { icon: "pi pi-check-circle", text: "One-click audits of entire repositories" },
        { icon: "pi pi-file", text: "Non-technical reports" },
        { icon: "pi pi-chart-line", text: "Actionable insights and metrics" }
      ]
    },
    complete: {
      title: "Get a comprehensive view of your technical assets.",
      features: [
        { icon: "pi pi-code", text: "Deep code analysis" },
        { icon: "pi pi-sitemap", text: "Architecture assessment" },
        { icon: "pi pi-shield", text: "Security vulnerability scanning" }
      ]
    },
    secure: {
      title: "Your code security is our top priority.",
      features: [
        { icon: "pi pi-lock", text: "End-to-end encryption" },
        { icon: "pi pi-eye-slash", text: "Private code scanning" },
        { icon: "pi pi-key", text: "Secure access controls" }
      ]
    }
  };

  const navigate = useNavigate();

  const handleTryDemo = () => {
    navigate('/demo');
  };

  return (
    <div className="feature-section">
      <div className="feature-content">
        <div className="feature-text">
          <h1>A <span className="gradient-text">full spectrum</span> analysis at your fingertips</h1>
          
          <div className="feature-buttons">
            <button 
              className={`feature-button ${activeFeature === 'easy' ? 'active' : ''}`}
              onClick={() => setActiveFeature('easy')}
            >
              easy
            </button>
            <button 
              className={`feature-button ${activeFeature === 'complete' ? 'active' : ''}`}
              onClick={() => setActiveFeature('complete')}
            >
              complete
            </button>
            <button 
              className={`feature-button ${activeFeature === 'secure' ? 'active' : ''}`}
              onClick={() => setActiveFeature('secure')}
            >
              secure
            </button>
          </div>

          <div className="feature-description">
            <h3>{featureContent[activeFeature].title}</h3>
            <div className="feature-list">
              {featureContent[activeFeature].features.map((feature, index) => (
                <div key={index} className="feature-list-item">
                  <i className={feature.icon}></i>
                  <h2>{feature.text}</h2>
                </div>
              ))}
            </div>
          </div>
        </div>
        
        <div className="feature-image-container">
          <div className="feature-image">
            <img src={hero_1} alt="Feature visualization" loading="lazy"/>
          </div>
          <button className="feature-cta-button" onClick={handleTryDemo}>
            Try Demo
          </button>
        </div>
      </div>
    </div>
  );
};

const AuditCard = ({ audit, onAuditClick }) => (
  <div className="audit-card" onClick={() => onAuditClick(audit.url)}>
    <div className="audit-card-content">
      <img src={audit.logo} alt={audit.name} className="audit-logo" loading="lazy"/>
      <a href={audit.repoUrl} className="audit-repo-link" onClick={(e) => e.stopPropagation()}>
        {audit.repoUrl}
      </a>
      <div className="audit-stats">
        <span>{audit.linesOfCode.toLocaleString()} lines of code analyzed</span>
      </div>
    </div>
  </div>
);

const AuditsSectionWithCTA = () => {
  const navigate = useNavigate();
  const [isVisible, setIsVisible] = useState(false);
  const sectionRef = useRef(null);
  const hasAnimated = useRef(false);

  const audits = [
    {
      name: 'Redis',
      logo: Redis,
      repoUrl: 'https://github.com/redis/redis',
      linesOfCode: 310716,
      url: '/9ed79825-92eb-41a5-be92-d47f978d28d2/audit-summary'
    },
    {
      name: 'FastAPI',
      logo: FastAPI,
      repoUrl: 'https://github.com/tiangolo/fastapi',
      linesOfCode: 81016,
      url: '/f910c1c1-40a6-488e-a2a7-b7200383bc1c/audit-summary'
    },
    {
      name: 'Axios',
      logo: Axios,
      repoUrl: 'https://github.com/axios/axios',
      linesOfCode: 27743,
      url: '/223a1ddd-5f13-486d-8dd3-79e1c5c53d9d/audit-summary'
    }
  ];

  useEffect(() => {
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting && !hasAnimated.current) {
          setIsVisible(true);
          hasAnimated.current = true;
        }
      },
      {
        threshold: 0.3
      }
    );

    if (sectionRef.current) {
      observer.observe(sectionRef.current);
    }

    return () => {
      if (sectionRef.current) {
        observer.unobserve(sectionRef.current);
      }
    };
  }, []);

  const handleAuditClick = (url) => {
    navigate(url);
  };

  const handleStartTrial = () => {
    navigate('/register');
  };

  const handleLearnPricing = () => {
    navigate('/pricing');
  };

  const handleDiscoverMore = () => {
    navigate('/discover');
  };

  return (
    <div className="audits-with-cta" ref={sectionRef}>
      <div className="audits-block">
        <div className="audits-content">
          <div className="audits-text">
            <h2>Solidify your investment case on shared insights</h2>
            <p>Share and distribute the audit report with peers or make it public for maximum transparency</p>

            <div className="discover-more-button" style={{marginTop: '24px'}}>
              <button className="discover-more-button-button" onClick={handleDiscoverMore}>Discover audits</button>
            </div>
          </div>
          <div className="audits-examples-container">
            <h2>See CodeDD in action</h2>
            <div className="audit-cards-container">
              {audits.map((audit, index) => (
                <div 
                  key={audit.name}
                  className={`audit-card-wrapper ${isVisible ? 'visible' : ''}`}
                  style={{ 
                    transitionDelay: `${index * 0.5}s`,
                    marginRight: !isVisible ? '-24px' : '0'
                  }}
                >
                  <AuditCard audit={audit} onAuditClick={handleAuditClick} />
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      <div className="cta-container">
        <div className="cta-content">
          <h2 className="cta-gradient-title">Ready to get started?</h2>
          
          <div className="cta-grid">
            <div className="cta-left">
              <p>See what you can do with AI-powered software due diligence</p>
              <button 
                className="cta-primary-button"
                onClick={handleStartTrial}
              >
                Start free trial
              </button>
            </div>
            
            <div className="cta-right">
              <p>Find out what plan works best for your team</p>
              <h2 
                className="pricing-link"
                onClick={handleLearnPricing}
              >
                Learn about pricing
              </h2>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default function Start() {
  const [scrollPercentage, setScrollPercentage] = useState(0);
  const scrollContainerRef = useRef(null);
  const navigate = useNavigate();
  const [isDragging, setIsDragging] = useState(false);
  const [startX, setStartX] = useState(0);
  const [scrollLeft, setScrollLeft] = useState(0);

  const heroContent = {
    title: "AI-powered Software Due Diligence",
    description: "CodeDD is the easiest, most comprehensive and safest code auditing platform",
    buttonText: "Start free trial",
    demoButtonText: "Try Demo"
  };

  const heroCardContent = {
    title: "Data-driven insights at a glance",
    description: "Our AI-powered analysis provides immediate visibility into metrics that matter most for your technical investments.",
  };

  const handleScroll = () => {
    if (scrollContainerRef.current) {
      const { scrollLeft, scrollWidth, clientWidth } = scrollContainerRef.current;
      const newScrollPercentage = (scrollLeft / (scrollWidth - clientWidth)) * 100;
      setScrollPercentage(newScrollPercentage);
    }
  };

  useEffect(() => {
    const scrollContainer = scrollContainerRef.current;
    if (scrollContainer) {
      scrollContainer.addEventListener('scroll', handleScroll);
      return () => scrollContainer.removeEventListener('scroll', handleScroll);
    }
  }, []);

  const handleMouseDown = (e) => {
    setIsDragging(true);
    setStartX(e.pageX - scrollContainerRef.current.offsetLeft);
    setScrollLeft(scrollContainerRef.current.scrollLeft);
  };

  const handleMouseUp = () => {
    setIsDragging(false);
  };

  const handleMouseMove = (e) => {
    if (!isDragging) return;
    e.preventDefault();
    const x = e.pageX - scrollContainerRef.current.offsetLeft;
    const distance = (x - startX) * 2; // Adjust multiplier for faster/slower scrolling
    scrollContainerRef.current.scrollLeft = scrollLeft - distance;
  };

  const handleTouchStart = (e) => {
    setIsDragging(true);
    setStartX(e.touches[0].pageX - scrollContainerRef.current.offsetLeft);
    setScrollLeft(scrollContainerRef.current.scrollLeft);
  };

  const handleTouchMove = (e) => {
    if (!isDragging) return;
    const x = e.touches[0].pageX - scrollContainerRef.current.offsetLeft;
    const distance = (x - startX) * 2; // Adjust multiplier for faster/slower scrolling
    scrollContainerRef.current.scrollLeft = scrollLeft - distance;
  };

  const scrollTo = (direction) => {
    if (scrollContainerRef.current) {
      const { clientWidth } = scrollContainerRef.current;
      scrollContainerRef.current.scrollBy({ left: direction * clientWidth, behavior: 'smooth' });
    }
  };

  const handleStartFreeTrial = () => {
    navigate('/register');
  };

  const handleTryDemo = () => {
    navigate('/demo');
  };

  return (
    <div className="hero-main-content">
      <div className="hero-section">
        <div className="hero-content">
          <div className="hero-title-container">
            <h1 className="hero-title" style={{marginBottom: '24px'}}>{heroContent.title}</h1>
            <p className="hero-description" style={{marginBottom: '24px'}}>{heroContent.description}</p>
            <div className="hero-buttons">
              <button className="hero-cta-button" onClick={handleStartFreeTrial}>{heroContent.buttonText}</button>
              <button className="hero-secondary-button" onClick={handleTryDemo}>{heroContent.demoButtonText}</button>
            </div>
          </div>
          <div className="hero-3d-card-container">
            <HeroCard3D 
              title={heroCardContent.title}
              description={heroCardContent.description}
            />
          </div>
        </div>
      </div>
      <IntroBlock />
      <FeatureSection />
      <AuditsSectionWithCTA />
    </div>
  );
}
