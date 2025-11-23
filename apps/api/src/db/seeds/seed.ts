import { PrismaClient } from '@prisma/client';

const prisma = new PrismaClient();

async function main() {
  try {
    // Create sample events
    const eventsData = [
      {
        title: 'Geminids Meteor Shower',
        description: 'Annual Geminids meteor shower peak — excellent for meteor observations.',
        start: new Date('2025-12-13T00:00:00.000Z'),
        end: new Date('2025-12-14T23:59:59.000Z'),
        type: 'METEOR_SHOWER',
        lat: 16.3067,
        lon: 80.4365,
        locationName: 'Guntur Region, India',
        visibilityScore: 0.0
      },
      {
        title: 'Lunar Eclipse',
        description: 'Total lunar eclipse visible in parts of Asia and Australia.',
        start: new Date('2025-03-14T00:00:00.000Z'),
        end: new Date('2025-03-14T06:00:00.000Z'),
        type: 'LUNAR_ECLIPSE',
        lat: 16.3067,
        lon: 80.4365,
        locationName: 'Guntur Region, India',
        visibilityScore: 0.0
      }
    ];

    for (const ev of eventsData) {
      await prisma.event.upsert({
        where: { title: ev.title },
        update: ev,
        create: ev
      });
    }

    // Create sample dark sites near Guntur, India (realistic coordinates)
    const darkSitesData = [
      {
        name: 'Kolleru Viewpoint',
        lat: 16.3458,
        lon: 80.6789,
        lightPollution: 0.12,
        description: 'Open fields near Kolleru with lower light pollution.'
      },
      {
        name: 'Prakasam Hill Outskirts',
        lat: 16.2504,
        lon: 80.4501,
        lightPollution: 0.15,
        description: 'Higher elevation outskirts offering darker skies.'
      },
      {
        name: 'Chilakaluripet Farmlands',
        lat: 16.0650,
        lon: 80.2367,
        lightPollution: 0.10,
        description: 'Rural farmlands to the southwest with good horizon views.'
      }
    ];

    for (const ds of darkSitesData) {
      await prisma.darkSite.upsert({
        where: { name: ds.name },
        update: ds,
        create: ds
      });
    }

    // Create sample badges
    const badgesData = [
      {
        name: 'First Light',
        description: 'Awarded for the first verified stargazing visit.',
        iconUrl: '',
        pointsRequired: 0
      },
      {
        name: 'Stargazer',
        description: 'Awarded for accumulating 100 points.',
        iconUrl: '',
        pointsRequired: 100
      },
      {
        name: 'Astronomer',
        description: 'Awarded for accumulating 500 points.',
        iconUrl: '',
        pointsRequired: 500
      }
    ];

    for (const b of badgesData) {
      await prisma.badge.upsert({
        where: { name: b.name },
        update: b,
        create: b
      });
    }

    console.log('Seeding completed successfully.');
  } catch (error) {
    console.error('Error during seeding:', error);
    process.exitCode = 1;
  } finally {
    await prisma.$disconnect();
  }
}

main();
