import { Metadata } from 'next';
import { setRequestLocale } from 'next-intl/server';
import MosquesClient from './MosquesClient';

export const metadata: Metadata = {
  title: 'Moskeeën - VGM Gent',
  description: 'Ontdek alle moskeeën in Gent met gedetailleerde informatie, gebedstijden en faciliteiten.',
};

export default function MosquesPage({
  params: { locale }
}: {
  params: { locale: string };
}) {
  setRequestLocale(locale);
  
  return <MosquesClient />;
}