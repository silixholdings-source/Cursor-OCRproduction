'use server';
 
import {cookies} from 'next/headers';
import {Locale, defaultLocale} from './config';
 
const COOKIE_NAME = 'NEXT_LOCALE';
 
export async function getUserLocale(): Promise<Locale> {
  return cookies().get(COOKIE_NAME)?.value as Locale || defaultLocale;
}
 
export async function setUserLocale(locale: Locale) {
  cookies().set(COOKIE_NAME, locale);
}


