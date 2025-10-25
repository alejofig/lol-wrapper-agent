/**
 * Componente de carrusel para mostrar las maestrías más altas
 */

import Slider from "react-slick";
import "slick-carousel/slick/slick.css";
import "slick-carousel/slick/slick-theme.css";

interface Mastery {
  champion?: string;
  championLevel: number;
  championPoints: number;
  tokensEarned?: number;
  splash?: string;
}

interface MasteriesCarouselProps {
  masteries: Mastery[];
}

export default function MasteriesCarousel({ masteries }: MasteriesCarouselProps) {
  const topMasteries = masteries.slice(0, 5);

  if (topMasteries.length === 0) {
    return null;
  }

  // Componentes personalizados para las flechas sin texto
  const CustomPrevArrow = (props: any) => {
    const { onClick } = props;
    return (
      <button
        className="custom-prev-arrow"
        onClick={onClick}
        aria-label="Anterior"
        type="button"
      >
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
          <path d="M15 18L9 12L15 6" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
        </svg>
      </button>
    );
  };

  const CustomNextArrow = (props: any) => {
    const { onClick } = props;
    return (
      <button
        className="custom-next-arrow"
        onClick={onClick}
        aria-label="Siguiente"
        type="button"
      >
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
          <path d="M9 18L15 12L9 6" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
        </svg>
      </button>
    );
  };

  const settings = {
    centerMode: true,
    infinite: true,
    centerPadding: '0px',
    slidesToShow: 3,
    speed: 600,
    focusOnSelect: true,
    arrows: true,
    dots: false,
    autoplay: false,
    swipeToSlide: true,
    prevArrow: <CustomPrevArrow />,
    nextArrow: <CustomNextArrow />,
    responsive: [
      {
        breakpoint: 768,
        settings: {
          slidesToShow: 1,
          centerMode: false,
          centerPadding: '0px',
        }
      }
    ]
  };

  const formatPoints = (points: number) => {
    if (points >= 1000000) {
      return `${(points / 1000000).toFixed(1)}M`;
    } else if (points >= 1000) {
      return `${(points / 1000).toFixed(0)}K`;
    }
    return points.toLocaleString();
  };

  return (
    <div className="masteries-carousel">
      <Slider {...settings}>
        {topMasteries.map((mastery, index) => (
          <div key={index} className="mastery-slide-wrapper">
            <div className="mastery-slide">
              {mastery.splash && (
                <img
                  src={mastery.splash}
                  alt={mastery.champion || `Campeón ${index + 1}`}
                  className="mastery-splash"
                />
              )}
              <div className="mastery-overlay">
                <div className="mastery-level">M{mastery.championLevel}</div>
                <h4>{mastery.champion || `Campeón ${index + 1}`}</h4>
                <p>{formatPoints(mastery.championPoints)} puntos</p>
                {mastery.tokensEarned && mastery.tokensEarned > 0 && (
                  <div className="mastery-tokens">🎖️ {mastery.tokensEarned}</div>
                )}
              </div>
            </div>
          </div>
        ))}
      </Slider>

      {/* Estilos del carrusel */}
      <style>{`
        .masteries-carousel {
          width: 100%;
          max-width: 1000px;
          margin: 0 auto 22px;
          position: relative;
          background: radial-gradient(ellipse at center, rgba(200, 155, 60, 0.1) 0%, rgba(15, 35, 65, 0.2) 50%, rgba(0, 9, 19, 0.3) 100%);
          padding: 20px 60px;
          border-radius: 20px;
        }

        /* Estilos para react-slick */
        .masteries-carousel .slick-slider {
          position: relative;
        }

        .masteries-carousel .slick-list {
          margin: 0 -8px;
        }

        .masteries-carousel .slick-track {
          display: flex;
          align-items: center;
        }

        .masteries-carousel .slick-slide {
          padding: 0 8px;
          transition: all 0.6s cubic-bezier(0.25, 0.1, 0.25, 1);
          transform: scale(0.85);
          opacity: 0.6;
        }

        .masteries-carousel .slick-center {
          transform: scale(1.07);
          opacity: 1;
        }

        .mastery-slide-wrapper {
          outline: none;
          height: 360px;
          display: flex !important;
          align-items: center;
          justify-content: center;
        }

        .mastery-slide {
          background: linear-gradient(145deg, rgba(1, 10, 19, 0.9), rgba(15, 35, 65, 0.8));
          border: 2px solid rgba(200, 155, 60, 0.3);
          border-radius: 12px;
          width: 200px;
          max-width: 260px;
          box-sizing: border-box;
          box-shadow: 
            0 4px 20px rgba(0, 9, 19, 0.6),
            inset 0 1px 0 rgba(200, 155, 60, 0.2);
          transition: all 0.6s cubic-bezier(0.25, 0.1, 0.25, 1);
          overflow: hidden;
          position: relative;
          cursor: pointer;
        }

        .masteries-carousel .slick-center .mastery-slide {
          width: 350px;
          max-width: 400px;
          border: 3px solid rgba(200, 155, 60, 0.8);
          box-shadow: 
            0 8px 40px rgba(200, 155, 60, 0.4),
            0 0 80px rgba(15, 35, 65, 0.6),
            inset 0 1px 0 rgba(200, 155, 60, 0.4);
        }

        .mastery-splash {
          width: 100%;
          height: 240px;
          object-fit: cover;
          object-position: center;
          display: block;
          border-radius: 8px;
          transition: all 0.6s cubic-bezier(0.25, 0.1, 0.25, 1);
          background: linear-gradient(135deg, rgba(15, 35, 65, 0.3), rgba(200, 155, 60, 0.1));
          filter: brightness(0.9) contrast(1.1);
        }

        .masteries-carousel .slick-center .mastery-splash {
          height: 280px;
          filter: brightness(1) contrast(1.2) saturate(1.1);
          box-shadow: 
            0 0 30px rgba(200, 155, 60, 0.4),
            inset 0 0 50px rgba(15, 35, 65, 0.2);
        }

        .masteries-carousel .slick-slide:not(.slick-center) .mastery-splash {
          filter: blur(0.5px) grayscale(0.35) brightness(0.83);
          box-shadow: 0 2px 10px 2px rgba(110,110,130,0.07);
        }

        .mastery-overlay {
          padding: 15px 10px 18px 10px;
          text-align: center;
          background: linear-gradient(to bottom, 
            rgba(0, 9, 19, 0.2) 0%, 
            rgba(1, 10, 19, 0.8) 40%, 
            rgba(0, 9, 19, 0.95) 100%);
          color: #F0E6D2;
          font-family: 'Arial', 'Helvetica', sans-serif;
          letter-spacing: 0.05em;
          position: absolute;
          bottom: 0;
          left: 0;
          right: 0;
          border-radius: 0 0 8px 8px;
          border-top: 1px solid rgba(200, 155, 60, 0.3);
        }

        .mastery-level {
          position: absolute;
          top: 8px;
          right: 8px;
          background: linear-gradient(145deg, rgba(200, 155, 60, 0.9), rgba(200, 155, 60, 0.7));
          color: #0F2341;
          padding: 4px 8px;
          border-radius: 12px;
          font-size: 0.7rem;
          font-weight: 800;
          text-shadow: none;
          box-shadow: 
            0 2px 8px rgba(0, 9, 19, 0.4),
            inset 0 1px 0 rgba(255, 255, 255, 0.2);
        }

        .masteries-carousel .slick-center .mastery-level {
          font-size: 0.8rem;
          padding: 6px 12px;
        }

        .masteries-carousel .slick-center .mastery-overlay h4 {
          font-size: 1.2rem;
          font-weight: 800;
          margin: 0 0 6px 0;
          color: #C89B3C;
          text-shadow: 
            0 0 10px rgba(200, 155, 60, 0.8),
            0 2px 4px rgba(0, 9, 19, 0.9);
          text-transform: uppercase;
        }

        .masteries-carousel .slick-center .mastery-overlay p {
          font-size: 1.1rem;
          font-weight: 600;
          margin: 0;
          color: #A09B8C;
          text-shadow: 0 1px 3px rgba(0, 9, 19, 0.8);
        }

        .mastery-overlay h4 {
          font-size: 1rem;
          font-weight: 700;
          margin: 0 0 4px 0;
          color: #C8AA6E;
          text-shadow: 
            0 0 5px rgba(200, 170, 110, 0.6),
            0 1px 3px rgba(0, 9, 19, 0.8);
          text-transform: uppercase;
        }

        .mastery-overlay p {
          font-size: 0.95rem;
          font-weight: 500;
          margin: 0;
          color: #A09B8C;
          text-shadow: 0 1px 2px rgba(0, 9, 19, 0.7);
        }

        .mastery-tokens {
          margin-top: 4px;
          font-size: 0.8rem;
          color: #C89B3C;
          font-weight: 600;
          text-shadow: 0 0 5px rgba(200, 155, 60, 0.6);
        }

        .masteries-carousel .slick-center .mastery-tokens {
          font-size: 0.9rem;
          margin-top: 6px;
        }

        /* Estilos para las flechas personalizadas */
        .masteries-carousel .custom-prev-arrow,
        .masteries-carousel .custom-next-arrow {
          background: linear-gradient(145deg, rgba(1, 10, 19, 0.8), rgba(15, 35, 65, 0.6));
          border: 2px solid rgba(200, 155, 60, 0.4);
          border-radius: 50%;
          width: 55px;
          height: 55px;
          display: flex;
          align-items: center;
          justify-content: center;
          color: #C8AA6E;
          cursor: pointer;
          z-index: 3;
          position: absolute;
          top: 50%;
          transform: translateY(-50%);
          transition: all 0.3s cubic-bezier(0.25, 0.1, 0.25, 1);
          backdrop-filter: blur(15px);
          box-shadow: 
            0 4px 15px rgba(0, 9, 19, 0.5),
            0 0 20px rgba(200, 155, 60, 0.2),
            inset 0 1px 0 rgba(200, 155, 60, 0.3);
        }

        .masteries-carousel .custom-prev-arrow:hover,
        .masteries-carousel .custom-next-arrow:hover {
          background: linear-gradient(145deg, rgba(15, 35, 65, 0.9), rgba(200, 155, 60, 0.1));
          border-color: rgba(200, 155, 60, 0.8);
          color: #C89B3C;
          transform: translateY(-50%) scale(1.1);
          box-shadow: 
            0 6px 25px rgba(0, 9, 19, 0.7),
            0 0 30px rgba(200, 155, 60, 0.5),
            inset 0 1px 0 rgba(200, 155, 60, 0.5);
        }

        .masteries-carousel .custom-prev-arrow {
          left: -40px;
        }

        .masteries-carousel .custom-next-arrow {
          right: -40px;
        }

        /* Responsive */
        @media (max-width: 768px) {
          .masteries-carousel {
            padding: 15px 20px;
            margin: 0 auto 15px;
            max-width: 95%;
          }
          
          .masteries-carousel .slick-list {
            margin: 0;
          }
          
          .masteries-carousel .slick-slide {
            padding: 0;
            transform: scale(1);
            opacity: 1;
          }
          
          .masteries-carousel .custom-prev-arrow {
            left: -15px;
            width: 40px;
            height: 40px;
          }
          
          .masteries-carousel .custom-next-arrow {
            right: -15px;
            width: 40px;
            height: 40px;
          }
          
          .masteries-carousel .custom-prev-arrow svg,
          .masteries-carousel .custom-next-arrow svg {
            width: 18px;
            height: 18px;
          }
          
          .mastery-slide {
            width: 100%;
            max-width: 280px;
            margin: 0 auto;
            border-width: 2px;
          }
          
          .mastery-slide-wrapper {
            height: 300px;
          }
          
          .mastery-splash {
            height: 200px;
          }
          
          .masteries-carousel .slick-center .mastery-splash {
            height: 230px;
          }
          
          .mastery-overlay {
            padding: 12px 8px 15px 8px;
          }
          
          .mastery-level {
            font-size: 0.6rem;
            padding: 3px 6px;
          }
          
          .masteries-carousel .slick-center .mastery-overlay h4 {
            font-size: 1.2rem;
          }
          
          .mastery-overlay h4 {
            font-size: 1rem;
          }
        }
      `}</style>
    </div>
  );
}
