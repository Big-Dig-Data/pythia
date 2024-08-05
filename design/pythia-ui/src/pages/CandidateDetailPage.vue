<i18n src="../locales/availability.yaml"></i18n>
<i18n src="../locales/common.yaml"></i18n>
<i18n>
en:
  candidate_updated: Candidate successfuly updated
  since: Since
  all: All
  subjects: Subjects
  authors: Authors
  publisher: Publisher
  languages: Languages
  availability: Availability
  score_breakdown: Score breakdown
  score_info: How much individual authors, publishers, topics and languages contribute to the candidate score
  total: Total
  google_search: Open Google search for this title
  product_format: Product format
cs:
  candidate_updated: Kadidát byl úspěšně aktualizován
  since: od
  all: Všechno
  subjects: Témata
  authors: Autoři
  publisher: Vydavatelé
  languages: Jazyk
  availability: Dostupnost
  score_breakdown: Rozpad skóre
  score_info: Jak moc jednotliví autoři, vydavatelé, témata a jazyky přispívají ke skóre tohoto kandidáta
  total: Celkové skóre
  google_search: Otevřít Google vyhledávání pro tento titul
  product_format: Formát
</i18n>
<template>
  <div>
    <v-card class="float-right ma-2 pa-2 text-center" v-if="candidate">
      <v-card-text>
        <div>
          <v-btn
            icon
            color="blue lighten-2"
            @click="toggleLike(candidate, 'like')"
            class="mr-6"
          >
            <v-icon>
              {{ `${candidate.liked ? "fas" : "far"} fa-thumbs-up` }}
            </v-icon>
          </v-btn>
          <v-btn
            icon
            color="red lighten-2"
            @click="toggleLike(candidate, 'dislike')"
          >
            <v-icon>
              {{ `${candidate.disliked ? "fas" : "far"} fa-thumbs-down` }}
            </v-icon>
          </v-btn>
        </div>
        <div class="pt-6">
          <v-btn
            outlined
            color="info"
            :href="googleSearch"
            target="_blank"
            rel="noreferrer noopener"
          >
            <v-tooltip bottom>
              <template v-slot:activator="{ on }">
                <span v-on="on">
                  <v-icon>fab fa-google</v-icon> {{ $t("search") }}
                </span>
              </template>
              <span>{{ $t("google_search") }}</span>
            </v-tooltip>
          </v-btn>
        </div>
      </v-card-text>
    </v-card>

    <v-container fluid v-if="candidate">
      <v-row>
        <v-col>
          <h1 class="display-1">{{ candidate.title }}</h1>
        </v-col>
      </v-row>
      <v-row>
        <v-col>
          <table class="header">
            <tr>
              <th class="label">{{ $t("authors") }}:</th>
              <td>
                <span
                  v-for="author in candidate.authors"
                  :key="author.pk"
                  class="author"
                  >{{ author.name }}</span
                >
              </td>
            </tr>
            <tr>
              <th class="label">{{ $t("columns.publication_year") }}:</th>
              <td>{{ candidate.publication_year }}</td>
            </tr>
            <tr>
              <th class="label">ISBN:</th>
              <td>{{ candidate.isbn }}</td>
            </tr>
            <tr>
              <th class="label">{{ $t("columns.price") }}:</th>
              <td>
                {{ candidate.price }}
                {{ candidate.price_currency }}
              </td>
            </tr>
            <tr>
              <th class="label">{{ $t("availability") }}:</th>
              <td>{{ $t(candidate.availability) }}</td>
            </tr>
            <tr>
              <th class="label">{{ $t("product_format") }}:</th>
              <td>{{ getCandidateFormat(candidate.product_format) }}</td>
            </tr>
            <tr>
              <th class="label">{{ $t("columns.abstract") }}:</th>
              <td></td>
            </tr>
          </table>
          <p class="abstract">{{ candidate.abstract }}</p>
        </v-col>
      </v-row>
      <v-row>
        <v-col class="text-center">
          <h2>{{ $t("score_breakdown") }}</h2>
          <p>{{ $t("score_info") }}</p>
        </v-col>
      </v-row>
      <v-row>
        <v-col v-for="topic in ['authors', 'subjects']" :key="topic" cols="6">
          <v-card>
            <v-card-title>
              <span class="text-h5">{{ $t(topic) }}</span>
            </v-card-title>
            <v-card-text>
              <v-simple-table>
                <template v-slot:default>
                  <thead>
                    <tr>
                      <th>{{ $t(topic) }}</th>
                      <th v-for="yr in years" :key="yr">
                        {{ $t("columns.score") }} {{ $t("since") }} {{ yr }}
                      </th>
                      <th>{{ $t("total") }}</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="item in candidate[topic]" :key="item.pk">
                      <td>
                        <ExplicitTopicLink
                          :topic-type="topicToTopicType[topic]"
                          :topic-id="item.pk"
                        >
                          {{ item.name }}
                        </ExplicitTopicLink>
                      </td>
                      <td v-for="yr in years" :key="yr">
                        {{
                          format2SignificantPlaces(
                            item.normalized_score[`score_${yr}`] || 0
                          )
                        }}
                      </td>
                      <td>
                        {{
                          format2SignificantPlaces(
                            item.normalized_score.score_all || 0
                          )
                        }}
                      </td>
                    </tr>
                  </tbody>
                </template>
              </v-simple-table>
            </v-card-text>
          </v-card>
        </v-col>
      </v-row>
      <v-row>
        <v-col cols="6">
          <v-card>
            <v-card-title>
              <span class="text-h5">{{ $t("languages") }}</span>
            </v-card-title>
            <v-card-text>
              <v-simple-table>
                <template v-slot:default>
                  <thead>
                    <tr>
                      <th>{{ $t("languages") }}</th>
                      <th v-for="yr in years" :key="yr">
                        {{ $t("columns.score") }} {{ $t("since") }} {{ yr }}
                      </th>
                      <th>{{ $t("total") }}</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="item in candidate.languages" :key="item.pk">
                      <td>
                        <ExplicitTopicLink
                          topic-type="language"
                          :topic-id="item.pk"
                        >
                          {{ item.name }}
                        </ExplicitTopicLink>
                      </td>
                      <td v-for="yr in years" :key="yr">
                        {{
                          format2SignificantPlaces(
                            item.normalized_score[`score_${yr}`] || 0
                          )
                        }}
                      </td>
                      <td>
                        {{
                          format2SignificantPlaces(
                            item.normalized_score.score_all || 0
                          )
                        }}
                      </td>
                    </tr>
                  </tbody>
                </template>
              </v-simple-table>
            </v-card-text>
          </v-card>
        </v-col>
        <v-col cols="6">
          <v-card>
            <v-card-title>
              <span class="text-h5">{{ $t("publisher") }}</span>
            </v-card-title>
            <v-card-text>
              <v-simple-table>
                <template v-slot:default>
                  <thead>
                    <tr>
                      <th>{{ $t("publisher") }}</th>
                      <th v-for="yr in years" :key="yr">
                        {{ $t("columns.score") }} {{ $t("since") }} {{ yr }}
                      </th>
                      <th>{{ $t("total") }}</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr>
                      <td>
                        <ExplicitTopicLink
                          topic-type="publisher"
                          :topic-id="candidate.publisher.pk"
                        >
                          {{ candidate.publisher.name }}
                        </ExplicitTopicLink>
                      </td>
                      <td v-for="yr in years" :key="yr">
                        {{
                          format2SignificantPlaces(
                            candidate.publisher.normalized_score[
                              `score_${yr}`
                            ] || 0
                          )
                        }}
                      </td>
                      <td>
                        {{
                          format2SignificantPlaces(
                            candidate.publisher.normalized_score.score_all || 0
                          )
                        }}
                      </td>
                    </tr>
                  </tbody>
                </template>
              </v-simple-table>
            </v-card-text>
          </v-card>
        </v-col>
      </v-row>
    </v-container>
  </div>
</template>

<script>
import axios from "axios";
import { format2SignificantPlaces } from "../libs/numbers";
import { getCandidateFormat } from "../libs/candidateFormatCodelist";
import { mapActions } from "vuex";
import ExplicitTopicLink from "../components/ExplicitTopicLink";

export default {
  name: "CandidateDetailPage",
  components: { ExplicitTopicLink },
  props: { candidateId: { required: true, type: Number } },
  data() {
    return {
      candidate: null,
      years: [2000, 2005, 2010, 2015, 2020],
      topicToTopicType: { authors: "author", subjects: "psh" },
      googleSearchBase: "https://www.google.com/search?q=",
      googleSearch: null,
    };
  },

  methods: {
    ...mapActions({
      showSnackbar: "showSnackbar",
    }),
    format2SignificantPlaces,
    getCandidateFormat,

    async fetchCandidate() {
      try {
        const resp = await axios.get(`/api/candidates/${this.candidateId}/`);
        this.candidate = resp.data;
        this.candidate.availability = String(this.candidate.availability);
        if (this.candidate.availability.length < 2) {
          this.candidate.availability = "0" + this.candidate.availability;
        }
        this.googleSearch = `${this.googleSearchBase}"${this.candidate.isbn}"+${this.candidate.title}+${this.candidate.publisher.name}`;
      } catch (error) {
        this.showSnackbar({
          content: "Error fetching data: " + error,
          color: "error",
        });
        console.log("Error fetching data", error);
      }
    },

    async toggleLike(item, like) {
      const actionVal = item[`${like}d`] ? "remove" : "add";
      item[`${like}_disabled`] = true;
      try {
        const res = await axios.post(
          `/api/candidates/${this.candidate.pk}/${like}/`,
          {
            action_val: actionVal,
          }
        );
        if (res.status == 202) {
          item[`${like}d`] = !item[`${like}d`];
          this.showSnackbar({ content: this.$t("candidate_updated") });
        }
      } catch (error) {
        this.showSnackbar({
          content: "Error updating entry: " + error,
          color: "error",
        });
      }
    },
  },

  mounted() {
    this.fetchCandidate();
  },
};
</script>

<style lang="scss" scoped>
.abstract {
  max-width: 48rem;
}
.author {
  font-size: 100%;
  color: #000;
}

table.header {
  th.label {
    text-align: left;
    padding-right: 1rem;
    font-size: 100%;
    font-weight: 300;
  }
  td {
    font-weight: 500;
  }
}
</style>
