import { Metadata } from 'next';
import { notFound } from 'next/navigation';
import { setRequestLocale } from 'next-intl/server';
import MosqueDetailClient from './MosqueDetailClient';

export async function generateMetadata({ params }: { params: { id: string } }): Promise<Metadata> {
  return {
    title: `Moskee ${params.id} - VGM Gent`,
    description: `Informatie over moskee ${params.id} in Gent.`,
  };
}

export default async function MosqueDetailPage({
  params: { id, locale }
}: {
  params: { id: string; locale: string };
}) {
  setRequestLocale(locale);
  
  return <MosqueDetailClient mosqueId={id} />;
}