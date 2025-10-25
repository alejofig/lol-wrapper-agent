/**
 * Componente de carrusel para mostrar los campeones más jugados
 */

import Slider from "react-slick";
import "slick-carousel/slick/slick.css";
import "slick-carousel/slick/slick-theme.css";

interface Champion {
  champion: string;
  games: number;
  splash?: string;
}

interface ChampionsCarouselProps {
  champions: Champion[];
}

export default function ChampionsCarousel({ champions }: ChampionsCarouselProps) {
  const topChampions = champions.slice(0, 5);

  if (topChampions.length === 0) {
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

  return (
    <div className="champions-carousel">
      <Slider {...settings}>
        {topChampions.map((champ, index) => (
          <div key={index} className="champion-slide-wrapper">
            <div className="champion-slide">
              {champ.splash && (
                <img
                  src={champ.splash}
                  alt={champ.champion}
                  className="champion-splash"
                />
              )}
              <div className="champion-overlay">
                <h4>{champ.champion}</h4>
                <p>{champ.games} partidas</p>
              </div>
            </div>
          </div>
        ))}
      </Slider>

      {/* Estilos del carrusel */}
      <style>{`
        .champions-carousel {
          width: 100%;
          max-width: 1000px;
          margin: 0 auto 22px;
          position: relative;
          background: radial-gradient(ellipse at center, rgba(200, 155, 60, 0.1) 0%, rgba(15, 35, 65, 0.2) 50%, rgba(0, 9, 19, 0.3) 100%);
          padding: 20px 60px;
          border-radius: 20px;
        }

        /* Estilos para react-slick */
        .champions-carousel .slick-slider {
          position: relative;
        }

        .champions-carousel .slick-list {
          margin: 0 -8px;
        }

        .champions-carousel .slick-track {
          display: flex;
          align-items: center;
        }

        .champions-carousel .slick-slide {
          padding: 0 8px;
          transition: all 0.6s cubic-bezier(0.25, 0.1, 0.25, 1);
          transform: scale(0.85);
          opacity: 0.6;
        }

        .champions-carousel .slick-center {
          transform: scale(1.07);
          opacity: 1;
        }

        .champion-slide-wrapper {
          outline: none;
          height: 360px;
          display: flex !important;
          align-items: center;
          justify-content: center;
        }

        .champion-slide {
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

        .champions-carousel .slick-center .champion-slide {
          width: 350px;
          max-width: 400px;
          border: 3px solid rgba(200, 155, 60, 0.8);
          box-shadow: 
            0 8px 40px rgba(200, 155, 60, 0.4),
            0 0 80px rgba(15, 35, 65, 0.6),
            inset 0 1px 0 rgba(200, 155, 60, 0.4);
        }

        .champion-splash {
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

        .champions-carousel .slick-center .champion-splash {
          height: 280px;
          filter: brightness(1) contrast(1.2) saturate(1.1);
          box-shadow: 
            0 0 30px rgba(200, 155, 60, 0.4),
            inset 0 0 50px rgba(15, 35, 65, 0.2);
        }

        .champions-carousel .slick-slide:not(.slick-center) .champion-splash {
          filter: blur(0.5px) grayscale(0.35) brightness(0.83);
          box-shadow: 0 2px 10px 2px rgba(110,110,130,0.07);
        }

        .champion-overlay {
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

        .champions-carousel .slick-center .champion-overlay h4 {
          font-size: 1.2rem;
          font-weight: 800;
          margin: 0 0 6px 0;
          color: #C89B3C;
          text-shadow: 
            0 0 10px rgba(200, 155, 60, 0.8),
            0 2px 4px rgba(0, 9, 19, 0.9);
          text-transform: uppercase;
        }

        .champions-carousel .slick-center .champion-overlay p {
          font-size: 1.1rem;
          font-weight: 600;
          margin: 0;
          color: #A09B8C;
          text-shadow: 0 1px 3px rgba(0, 9, 19, 0.8);
        }

        .champion-overlay h4 {
          font-size: 1rem;
          font-weight: 700;
          margin: 0 0 4px 0;
          color: #C8AA6E;
          text-shadow: 
            0 0 5px rgba(200, 170, 110, 0.6),
            0 1px 3px rgba(0, 9, 19, 0.8);
          text-transform: uppercase;
        }

        .champion-overlay p {
          font-size: 0.95rem;
          font-weight: 500;
          margin: 0;
          color: #A09B8C;
          text-shadow: 0 1px 2px rgba(0, 9, 19, 0.7);
        }

        /* Estilos para las flechas personalizadas */
        .custom-prev-arrow,
        .custom-next-arrow {
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

        .custom-prev-arrow:hover,
        .custom-next-arrow:hover {
          background: linear-gradient(145deg, rgba(15, 35, 65, 0.9), rgba(200, 155, 60, 0.1));
          border-color: rgba(200, 155, 60, 0.8);
          color: #C89B3C;
          transform: translateY(-50%) scale(1.1);
          box-shadow: 
            0 6px 25px rgba(0, 9, 19, 0.7),
            0 0 30px rgba(200, 155, 60, 0.5),
            inset 0 1px 0 rgba(200, 155, 60, 0.5);
        }

        .custom-prev-arrow {
          left: -40px;
        }

        .custom-next-arrow {
          right: -40px;
        }

        /* Responsive */
        @media (max-width: 768px) {
          .champions-carousel {
            padding: 15px 20px;
            margin: 0 auto 15px;
            max-width: 95%;
          }
          
          .champions-carousel .slick-list {
            margin: 0;
          }
          
          .champions-carousel .slick-slide {
            padding: 0;
            transform: scale(1);
            opacity: 1;
          }
          
          .custom-prev-arrow {
            left: -15px;
            width: 40px;
            height: 40px;
          }
          
          .custom-next-arrow {
            right: -15px;
            width: 40px;
            height: 40px;
          }
          
          .custom-prev-arrow svg,
          .custom-next-arrow svg {
            width: 18px;
            height: 18px;
          }
          
          .champion-slide {
            width: 100%;
            max-width: 280px;
            margin: 0 auto;
            border-width: 2px;
          }
          
          .champion-slide-wrapper {
            height: 300px;
          }
          
          .champion-splash {
            height: 200px;
          }
          
          .champions-carousel .slick-center .champion-splash {
            height: 230px;
          }
          
          .champion-overlay {
            padding: 12px 8px 15px 8px;
          }
          
          .champions-carousel .slick-center .champion-overlay h4 {
            font-size: 1.2rem;
          }
          
          .champion-overlay h4 {
            font-size: 1rem;
          }
        }
      `}</style>
    </div>
  );
}
